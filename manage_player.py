import click
import json
import datetime
import os
import pathlib
import logging
import structlog
import sys
import time

from flask import Flask, request
from flask_restplus import Api, Resource
from requests import post, get, delete
from tqdm import tqdm

from audioutils.parallel import do_parallel_with_pbar
from audioutils.io import get_and_make_artist_and_album_dirs
from audioutils.conversion import convert_album


logfile_name = 'manage_player_log_{}.txt'.format(
    datetime.datetime.now()
)
logfile_path = os.path.join(
    pathlib.Path.home(),
    '.audioutils',
    'logs',
    logfile_name
)
logging.basicConfig(
    filename=logfile_path,
    level=logging.DEBUG    
)

from structlog.stdlib import LoggerFactory
from structlog.processors import (
    JSONRenderer,
    TimeStamper
)

structlog.configure(
    logger_factory=LoggerFactory(),
    processors=[TimeStamper(), JSONRenderer()]
)

LOGGER = structlog.get_logger()


def convert_and_save_album(
    source,
    target,
    target_format,
    bitrate,
    copy_non_sound,
    num_processes):

    print('Inside convert_and_save_album', file=sys.stderr)
    (artist, album) = source.split('/')[-2:]
    (artist_dir, album_dir) = get_and_make_artist_and_album_dirs(
        artist,
        album,
        target)
    print('Calling convert_album', file=sys.stderr)
    convert_album(
        album_dir,
        target_format,
        source,
        bitrate,
        copy_non_sound,
        num_processes)


def start_server(
    player_dir, 
    target_format, 
    bitrate, 
    copy_non_sound, 
    num_processes):

    app = Flask(__name__) 
    api = Api(app)
    sources = []
    completed = []

    @api.route('/add_source')
    class AddSource(Resource):
        
        def post(self): 
            
            source_path = request.form['source_path']

            LOGGER.info(
                'Adding source',
                source_path=source_path
            )

            sources.append(source_path)


    @api.route('/start_sync')
    class StartSync(Resource):
        
        def post(self):

            for s in sources:

                LOGGER.info(
                    'Converting and saving',
                    source_path=s
                )

                (artist, album) = s.split('/')[-2:]
                (artist_dir, album_dir) = get_and_make_artist_and_album_dirs(
                    artist,
                    album,
                    player_dir
                )
                convert_album(
                    album_dir,
                    target_format,
                    source,
                    bitrate,
                    copy_non_sound,
                    num_processes
                )
                completed.append(s)


    @api.route('/check_status')
    class CheckStatus(Resource):

        def delete(self):
            
            sources.clear()
            completed.clear()


        def get(self):
           
            return {
                'sources': sources,
                'completed': completed
            }


    app.run(host='127.0.0.1', port='5000', debug=True)


@click.group()
@click.pass_context
def player_cli(ctx):

    ctx.obj['base_url'] = 'http://127.0.0.1:5000/'


@player_cli.command()
@click.option('--player-dir')
@click.option('--target-format', default='mp3')
@click.option('--bitrate', default='128k')
@click.option('--copy-non-sound', default=False)
@click.option('--num-processes', default=1)
@click.pass_context
def initialize(
    ctx,
    player_dir,
    target_format,
    bitrate,
    copy_non_sound,
    num_processes):

    ctx.obj['player_dir'] = player_dir
    ctx.obj['target_format'] = target_format
    ctx.obj['bitrate'] = bitrate
    ctx.obj['copy_non_sound'] = copy_non_sound
    ctx.obj['num_processes'] = num_processes

    start_server(
        ctx.obj['player_dir'],
        ctx.obj['target_format'],
        ctx.obj['bitrate'],
        ctx.obj['copy_non_sound'],
        ctx.obj['num_processes']
    )


@player_cli.command('add-source')
@click.option('--source')
@click.pass_context
def add_source(ctx, source):

    add_source_url = ctx.obj['base_url'] + 'add_source'
    data = {'source_path': source}

    post(add_source_url, data=data)


@player_cli.command('start-sync')
@click.pass_context
def start_sync(ctx):

    start_sync_url = ctx.obj['base_url'] + 'start_sync' 
    check_status_url = ctx.obj['base_url'] + 'check_status'

    post(start_sync_url)

    status_check = json.loads(get(check_status_url).text)
    total = len(status_check['sources'])
    num_complete = len(status_check['completed'])

    with tqdm(total=total) as pbar:
        
        while num_complete < total:
            
            status_check = json.loads(get(check_status_url).text)
            new_num_complete = len(status_check['completed'])

            if new_num_complete > num_complete:
                pbar.update(new_num_complete - num_complete)

            num_complete = new_num_complete

            time.sleep(5)


@player_cli.command('clear')
@click.pass_context
def clear(ctx):

    check_status_url = ctx.obj['base_url'] + 'check_status' 

    delete(check_status_url)


if __name__ == '__main__':
    player_cli(obj={})
