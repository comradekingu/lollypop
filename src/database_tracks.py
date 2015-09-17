# Copyright (c) 2014-2015 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gettext import gettext as _
import itertools

from lollypop.define import Lp, Type
from lollypop.utils import translate_artist_name


class TracksDatabase:
    """
        All functions take a sqlite cursor as last parameter,
        set another one if you're in a thread
    """

    def __init__(self):
        """
            Init tracks database object
        """
        pass

    def add(self, name, filepath, duration, tracknumber, discnumber,
            album_id, year, popularity, ltime, mtime, sql=None):
        """
            Add a new track to database
            @param name as string
            @param filepath as string,
            @param duration as int
            @param tracknumber as int
            @param discnumber as int
            @param album_id as int
            @param genre_id as int
            @param year as int
            @param popularity as int
            @param ltime as int
            @param mtime as int
            @warning: commit needed
        """
        if not sql:
            sql = Lp.sql
        # Invalid encoding in filenames may raise an exception
        try:
            sql.execute(
                "INSERT INTO tracks (name, filepath, duration, tracknumber,\
                discnumber, album_id, year, popularity, ltime, mtime) VALUES\
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name,
                                                  filepath,
                                                  duration,
                                                  tracknumber,
                                                  discnumber,
                                                  album_id,
                                                  year,
                                                  popularity,
                                                  ltime,
                                                  mtime))
        except Exception as e:
            print("TracksDatabase::add: ", e, ascii(filepath))

    def add_artist(self, track_id, artist_id, sql=None):
        """
            Add artist to track
            @param track id as int
            @param artist id as int
            @warning: commit needed
        """
        if not sql:
            sql = Lp.sql
        artists = self.get_artist_ids(track_id, sql)
        if artist_id not in artists:
            sql.execute("INSERT INTO "
                        "track_artists (track_id, artist_id)"
                        "VALUES (?, ?)", (track_id, artist_id))

    def add_genre(self, track_id, genre_id, sql=None):
        """
            Add genre to track
            @param track id as int
            @param genre id as int
            @warning: commit needed
        """
        if not sql:
            sql = Lp.sql
        genres = self.get_genre_ids(track_id, sql)
        if genre_id not in genres:
            sql.execute("INSERT INTO "
                        "track_genres (track_id, genre_id)"
                        "VALUES (?, ?)", (track_id, genre_id))

    def get_ids_for_name(self, name, sql=None):
        """
            Return track ids with name
            @param name as str
            @return track id as int
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT rowid\
                              FROM tracks where name=? COLLATE NOCASE",
                             (name,))
        return list(itertools.chain(*result))

    def get_id_by_path(self, filepath, sql=None):
        """
            Return track id for path
            @param filepath as str
            @return track id as int
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT rowid FROM tracks where filepath=?",
                             (filepath,))
        v = result.fetchone()
        if v:
            return v[0]
        return None

    def get_name(self, track_id, sql=None):
        """
            Get track name for track id
            @param Track id as int
            @return Name as string
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT name FROM tracks where rowid=?",
                             (track_id,))
        v = result.fetchone()
        if v:
            return v[0]

        return ""

    def get_year(self, album_id, sql=None):
        """
            Get track year
            @param track id as int
            @return track year as string
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT year FROM tracks where rowid=?",
                             (album_id,))
        v = result.fetchone()
        if v and v[0]:
            return str(v[0])

        return ""

    def get_path(self, track_id, sql=None):
        """
            Get track path for track id
            @param Track id as int
            @return Path as string
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT filepath FROM tracks where rowid=?",
                             (track_id,))
        v = result.fetchone()
        if v:
            return v[0]

        return ""

    def get_album_id(self, track_id, sql=None):
        """
            Get album id for track id
            @param track id as int
            @return album id as int
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT album_id FROM tracks where rowid=?",
                             (track_id,))
        v = result.fetchone()
        if v:
            return v[0]

        return -1

    def get_album_name(self, track_id, sql=None):
        """
            Get album name for track id
            @param track id as int
            @return album name as str
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT albums.name from albums,tracks\
                              WHERE tracks.rowid=? AND\
                              tracks.album_id=albums.rowid", (track_id,))
        v = result.fetchone()
        if v:
            return v[0]

        return _("Unknown")

    def get_artist_ids(self, track_id, sql=None):
        """
            Get artist ids
            @param track id as int
            @return artist ids as [int]
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT artist_id FROM track_artists\
                              WHERE track_id=?", (track_id,))
        return list(itertools.chain(*result))

    def get_artist_names(self, track_id, sql=None):
        """
            Get artist names
            @param track id as int
            @return Genre name as str "artist1, artist2, ..."
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT name FROM artists, track_artists\
                              WHERE track_artists.track_id=?\
                              AND track_artists.artist_id=artists.rowid",
                             (track_id,))
        artists = [translate_artist_name(row[0]) for row in result]
        return ", ".join(artists)

    def get_genre_ids(self, track_id, sql=None):
        """
            Get genre ids
            @param track id as int
            @return genre ids as [int]
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT genre_id FROM track_genres\
                              WHERE track_id=?", (track_id,))
        return list(itertools.chain(*result))

    def get_genre_names(self, track_id, sql=None):
        """
            Get genre names
            @param track id as int
            @return Genre name as str "genre1, genre2..."
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT name FROM genres, track_genres\
                              WHERE track_genres.track_id=?\
                              AND track_genres.genre_id=genres.rowid",
                             (track_id,))
        genres = [row[0] for row in result]
        return ", ".join(genres)

    def get_mtimes(self, sql=None):
        """
            Get mtime for tracks
            WARNING: Should be called before anything is shown on screen
            @param None
            @return dict of {filepath as string: mtime as int}
        """
        if not sql:
            sql = Lp.sql
        mtimes = {}
        result = sql.execute("SELECT filepath, mtime FROM tracks")
        for row in result:
            mtimes.update((row,))
        return mtimes

    def get_infos(self, track_id, sql=None):
        """
            Get all track informations for track id
            @param Track id as int
            @return (name as string, filepath as string,
            duration as int, tracknumber as int, album_id as int)
            Returned values can be (None, None, None, None)
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT name, filepath,\
                              duration, album_id\
                              FROM tracks WHERE rowid=?", (track_id,))
        v = result.fetchone()
        if v:
            return v
        return (None, None, None, None)

    def get_album_artist_id(self, track_id, sql=None):
        """
            Get album_artist id for track id
            @param Track id as int
            @return Performer id as int
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT albums.artist_id from albums,tracks\
                              WHERE tracks.rowid=?\
                              AND tracks.album_id ==\
                              albums.rowid", (track_id,))
        v = result.fetchone()

        if v:
            return v[0]

        return Type.COMPILATIONS

    def get_paths(self, sql=None):
        """
            Get all tracks filepath
            @param None
            @return Array of filepath as string
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT filepath FROM tracks;")
        return list(itertools.chain(*result))

    def get_number(self, track_id, sql=None):
        """
            Get track position in album
            @param track id as int
            @return position as int
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT tracknumber FROM tracks\
                              WHERE rowid=?", (track_id,))
        v = result.fetchone()
        if v:
            return v[0]

        return 0

    def get_duration(self, track_id, sql=None):
        """
            Get track duration for track id
            @param Track id as int
            @return duration as int
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT duration FROM tracks\
                              WHERE rowid=?", (track_id,))
        v = result.fetchone()
        if v:
            return v[0]

        return 0

    def is_empty(self, sql=None):
        """
            Return True if no tracks in db
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT COUNT(*) FROM tracks  LIMIT 1")
        v = result.fetchone()
        if v:
            return v[0] == 0

        return True

    def get_as_non_album_artist(self, artist_id, sql=None):
        """
            Get tracks for artist_id where artist_id isn't main artist
            @param artist id as int
            @return list of [tracks id as int, track name as string]
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT tracks.rowid, tracks.name\
                              FROM tracks, track_artists, albums\
                              WHERE albums.rowid == tracks.album_id\
                              AND track_artists.artist_id=?\
                              AND track_artists.track_id=tracks.rowid\
                              AND albums.artist_id != ?", (artist_id,
                                                           artist_id))
        return list(result)

    def get_populars(self, sql=None):
        """
            Return most listened to tracks
            @return tracks as [int]
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT rowid FROM tracks\
                              WHERE popularity!=0\
                              ORDER BY popularity DESC LIMIT 100")
        return list(itertools.chain(*result))

    def get_avg_popularity(self, sql=None):
        """
            Return avarage popularity
            @return avarage popularity as int
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT AVG(popularity) FROM (SELECT popularity "
                             "FROM tracks ORDER BY POPULARITY DESC LIMIT 100)")
        v = result.fetchone()
        if v and v[0] > 5:
            return v[0]
        return 5

    def set_more_popular(self, track_id, sql=None):
        """
            Increment popularity field
            @param track id as int
            @raise sqlite3.OperationalError on db update
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT popularity from tracks WHERE rowid=?",
                             (track_id,))
        pop = result.fetchone()
        if pop:
            current = pop[0]
        else:
            current = 0
        current += 1
        sql.execute("UPDATE tracks set popularity=? WHERE rowid=?",
                    (current, track_id))
        sql.commit()

    def set_listened_at(self, track_id, time, sql=None):
        """
            Set ltime for track
            @param track id as int
            @param time as int
        """
        if not sql:
            sql = Lp.sql
        sql.execute("UPDATE tracks set ltime=? WHERE rowid=?",
                    (time, track_id))
        sql.commit()

    def get_never_listened_to(self, sql=None):
        """
            Return random tracks never listened to
            @return tracks as [int]
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT rowid FROM tracks\
                              WHERE ltime=0\
                              ORDER BY random() LIMIT 100")
        return list(itertools.chain(*result))

    def get_recently_listened_to(self, sql=None):
        """
            Return tracks listened recently
            @return tracks as [int]
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT rowid FROM tracks\
                              WHERE ltime!=0\
                              ORDER BY ltime DESC LIMIT 100")
        return list(itertools.chain(*result))

    def get_randoms(self, sql=None):
        """
            Return random tracks
            @return array of track ids as int
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT rowid FROM tracks\
                              ORDER BY random() LIMIT 100")
        return list(itertools.chain(*result))

    def set_ltime(self, track_id, ltime, sql=None):
        """
            Set ltime
            @param track id as int
            @param mtime as int
            @warning: commit needed
        """
        if not sql:
            sql = Lp.sql
        sql.execute("UPDATE tracks set ltime=? WHERE rowid=?",
                    (ltime, track_id))

    def set_popularity(self, track_id, popularity, commit=False, sql=None):
        """
            Set popularity
            @param track id as int
            @param popularity as int
            @warning: commit needed
        """
        if not sql:
            sql = Lp.sql
        try:
            sql.execute("UPDATE tracks set popularity=? WHERE rowid=?",
                        (popularity, track_id))
            if commit:
                sql.commit()
        except:  # Database is locked
            pass

    def get_popularity(self, track_id, sql=None):
        """
            Get popularity
            @param track id  as int
            @return popularity as int
        """
        if not sql:
            sql = Lp.sql
        result = sql.execute("SELECT popularity FROM tracks WHERE\
                             rowid=?", (track_id,))

        v = result.fetchone()
        if v:
            return v[0]
        return 0

    def clean(self, track_id, sql=None):
        """
            Clean database for track id
            @param track_id as int
            @warning commit needed
        """
        if not sql:
            sql = Lp.sql
        sql.execute("DELETE FROM track_artists\
                     WHERE track_id = ?", (track_id,))
        sql.execute("DELETE FROM track_genres\
                     WHERE track_id = ?", (track_id,))

    def search(self, searched, sql=None):
        """
            Search for tracks looking like searched
            @param searched as string
            return: list of [id as int, name as string]
        """
        if not sql:
            sql = Lp.sql

        result = sql.execute("SELECT rowid, name FROM tracks\
                              WHERE name LIKE ? LIMIT 25",
                             ('%' + searched + '%',))
        return list(result)

    def search_track(self, artist, title, sql=None):
        """
            Get track id for artist and title
            @param artist as string
            @param title as string
            @param sql as sqlite cursor
            @return track id as int
            @thread safe
        """
        if not sql:
            sql = Lp.sql
        track_ids = self.get_ids_for_name(title, sql)
        for track_id in track_ids:
            album_artist = self.get_album_artist_id(track_id, sql)
            album_artist_name = Lp.artists.get_name(album_artist, sql)
            if album_artist_name == artist:
                return track_id
            artist_name = Lp.tracks.get_artist_names(track_id, sql)
            if artist_name == artist:
                return track_id
        return None

    def remove(self, path, sql=None):
        """
            Remove track
            @param Track path as string
        """
        if not sql:
            sql = Lp.sql
        track_id = self.get_id_by_path(path, sql)
        sql.execute("DELETE FROM track_genres\
                     WHERE track_id=?", (track_id,))
        sql.execute("DELETE FROM track_artists\
                     WHERE track_id=?", (track_id,))
        sql.execute("DELETE FROM tracks\
                     WHERE rowid=?", (track_id,))