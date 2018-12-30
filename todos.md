# Database
* Should probably use Enum for some of the columns like "file_type"
* Set up explicit relations between AlbumRegistry, ArtistRegsistry, SongRegistry, etc. using `relationship` or `ForeignKey` or something like that.
* Consider schemaless for music metadata.
* Consider distributed database so the DB can be stored on my external drive.
* Include some functionality for updating a database from the local media dir, and call that in the database initialization tool.

# Usability
* Develop better way to deal with artist metadata (especially ID3 tag) and avoid explicitly specifying directories and songs. Maybe can integrate with Discogs API.
* Need a way to keep track of which things are on my list of stuff to listen to. Check if beet can do this with a playlist or something like that. OR randomly select a subset of stuff from my lib each time I change up my mp3 player.
* In general, would be cool to algorithmically select what gets loaded to my mp3 player.

# Logging
* Keep tuning and improving the logging. Structlog is really powerful. Let's use its capabilities fully where it helps.
