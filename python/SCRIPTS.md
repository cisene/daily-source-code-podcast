# Scripts

What the scripts in `python/` do and how to run them. This text was the
header comment of each script (moved here 2026-10-29, the comments were taken
out of the code). Run them from `python/`.

## Rebuilding the release

Episode data, in this order:

```
build-bonus-episodes.py --write --list
release-audio-names.py
update-episodes-enclosures.py --write
update-episodes-links.py --write
update-episodes-summaries.py --write
update-episodes-text.py --write
check-links.py
```

New transcripts: `srt-transcribe.py`, `srt-music.py` (analyse, apply),
`srt-fix-names.py`, `convert-srv-to-vtt.py`, `build-chapters.py --write`, then
`update-episodes-links.py --write`.

Stage and upload:

```
stage-release.py --write media srt vtt chapters opml
update-episodes-enclosures.py --write    # lengths from the staged copies
check-links.py
upload.py all                            # dry run
upload.py --go audio
upload.py --go video chapters srt vtt opml artwork
upload.py --go feed                      # last; refused until the rest is up
```

`upload.py` notes:

- The bucket is versioned and the key may not read object versions, so rclone
  runs with `--s3-no-head`: no read-back after an upload (it answered 403);
  S3's MD5 of the upload is checked instead.
- A file once up is never overwritten (`--ignore-existing`), only the feed.
  `--replace` for a deliberate fix, then a CloudFront invalidation.
- `DSC_ACL` sets an object ACL, `DSC_TRANSFERS` the parallel uploads (4).

`build.py` renders the feed (`../rss.xml`); `rss.xml` on the
host is that render.

## Per script


### archive-tag-enclosures.py

List the published enclosure urls named in the tags of the archive files.

From 2006 on the archive files carry the original post in their tags (TDES,
comment) with its "Direct link to the show", and often the item guid (TGID).
That names the feed item the file was published as, whatever date is in the
archive file name. Writes json/dsc-archive-tag-enclosures.json:

```
{ "2007/DSC-2007-12-04.mp3": { "title": ..., "urls": [...] }, ... }
```


The archive is only read (ffprobe).


### art-logo-2004-12.py

Vector reconstruction of the second Daily Source Code logo, made by Marchel
("Marchel made me a new logo for the source code, I love it!", blog
2004-12-06; in the mp3 tags 2004-12-07 .. 2005-10, 170x170): three slabs in
perspective, purple / light grey / purple, with "DAILY", "SOURCE", "CODE"
in extruded silver serif capitals.


```
art-logo-2004-12.py OUT.svg
```


The original is a 3D render; this is an approximation: each word is laid
out flat (Liberation Serif Bold, SIL OFL, as outlines) and every point is
mapped onto the slab's front face as measured on the original (scaled 4x,
680 x 680) by a perspective transform. The extrusion is a stack of dark
copies under a silver face. No font dependencies.


### art-logo-2004.py

Vector reconstruction of the first Daily Source Code logo: three tilted
bands, "DAILY" in a spaced bold italic serif and "CODE" in a wide square
sans, white on navy, with "SOURCE" in a condensed sans, navy on white.
Posted as an animation on 2004-09-09 (cloud2.urj.nl/acImages/2004/09/09/
dsc_anim-nonlooping.gif, 198x158, the bands slide in), in the mp3 tags
2004-11-16 .. 2004-12-06 (170x170 JPEG).


```
art-logo-2004.py OUT.svg [ASPECT [SCALE]]
```


ASPECT is the canvas shape (width/height, e.g. 1/1, 16/9, 9/16; default
1/1), SCALE the canvas height relative to the logo's square (default 1;
1.1 keeps the corners inside a circle crop).

Geometry measured on the last frame of the animation (palette colours, sharp
edges), scaled 4x and turned 7.9 degrees back to level (872 x 712). "DAILY" and "SOURCE" are glyph outlines of the
Liberation fonts (SIL OFL), each letter fitted to the box of the original
letter; "CODE" is drawn (rounded rectangles). The SVG has no font
dependencies.


### blog-posts.py

Collect Adam's blog posts (all categories, not only the Daily Source Code)
into json/blog-posts.json, as text: the travel posts say where he was.


```
blog-posts.py feeds               items of the saved feeds in rss/
blog-posts.py pages QUEUE.txt     pages fetched from the Wayback Machine,
                                  QUEUE.txt lines "URL FILE"
                                  (radio.weblogs.com/0001014/YYYY/MM/DD.html,
                                  www.curry.com/YYYY/MM/DD, curry.podshow.com)
```


Each post: date (YYYY-MM-DD, of the post), time (if known), permalink,
title, text (HTML removed), source (feed file or Wayback url). Posts are
merged by permalink, or by date and title.


### build-bonus-episodes.py

Bonus items from ../yaml/bonus-episodes.yaml: writes
../yaml/episodes/bonus-<id>.yaml (the episode format, itunes:episodeType
bonus, no episode number) and, with --list, the episode list of
../yaml/daily-source-code.yaml: every episode oldest first, a bonus item
after the last numbered show of its date or before.
Title, date, link and show notes come from the item's origin (a post in
json/dsc-posts-mirror.json, a blog post in json/blog-posts.json, or an item
of a saved feed); the manifest sets them when there is no origin.

Usage, from python/: build-bonus-episodes.py [--write] [--list]


### build-chapters.py

Chapters from a transcript. Breaks where the talk changes subject: lexical cohesion between
the two minutes before and after each 20 s block (TextTiling, lemmas and
spaCy word vectors), helped by Adam's transition phrases and by pauses; the
[ Music ] stretches of a minute or more are chapters of their own. Titles
from the names and terms a chapter uses most, weighed against all
transcripts. Writes JSON chapters 1.2.0 (podcastindex.org) to
../chapters/YEAR/<release name>.json, or a review sheet.

Usage, from python/, with the spaCy venv:

```
build-chapters.py --write [srt/YEAR/FILE.srt ...]
build-chapters.py OUTDIR srt/YEAR/FILE.srt ...   (review sheets)
```


### build-timeline.py

-*- coding: utf-8 -*-


### check-links.py

Every link to our host must point at a file that goes up: checks the urls on
thedailysourcecode.com (feed: base_url, and audio_url / video_url through
OP3) in ../yaml/daily-source-code.yaml and every episode yaml against the
files the stage holds or will hold (stage-release.py: audio, video, srt,
vtt, chapters, opml), the repo's artwork/ and the feed (/rss.xml, uploaded when
rendered). Also lists files that go up but nothing links (fine for opml).
Once the stage exists (upload.yaml: stage), every enclosure and
alternateEnclosure length must be the size of the staged file: the bucket
sits behind deep caches, so what goes up has to be right the first time.
Reads only.

Usage, from python/: check-links.py


### locations-build.py

Write yaml/locations.yaml: the curated entries (kept as they are, only
empty fields are filled), the places found in the shows (generated from

```
locations-geocode.py), and the recording periods (locations-timeline.py).
```



```
locations-build.py [--offline] [GEOCODED.json TIMELINE.json]
```


Lookups, for entries without coordinates:
- geonames id: from the GeoNames dump (offline, ~/.cache/geonames/),
- query: OpenStreetMap Nominatim (one request every PACE s, cached).
Altitude: GeoNames' elevation or DEM; else OpenTopoData's SRTM 30 m
(batches of 100 points, cached).
OpenStreetMap: Nominatim's result, or for a GeoNames place the OSM
relation Wikidata links to it (P1566 -> P402), else what Nominatim finds
by name within 25 km. --offline uses only what is in the cache and asks
no web service.

Only recording locations are kept: the curated entries, and the places

```
locations-timeline.py found a show to be recorded at (generated, rebuilt
```

on every run; set origin to curated to keep a hand edit). Names said as the
recording place that nothing resolves are kept with empty coordinates, to
resolve by hand.


### locations-extract.py

Find the places mentioned in the transcripts (srt/), the show notes
(shownotes/*.opml) and the episode descriptions (yaml/episodes/), with
spaCy's named entity recognizer (en_core_web_lg): GPE (countries, cities,
states), LOC (regions, mountains, waters), FAC (buildings, airports,
venues), and ORG when the name says it is a venue (hotels, clubs, studios
and the like are often tagged as organisations).


```
locations-extract.py OUT.json
```


OUT.json: {name: {label: count, ..., 'files': {file: count}}}. The names are
looked up later by locations-geocode.py. Needs spaCy (~/.cache/dsc-nlp-venv).


### locations-geocode.py

Look up the place names found by locations-extract.py in the GeoNames dump
(https://download.geonames.org/export/dump/, allCountries.txt and
alternateNamesV2.txt, WGS-84). Offline: the dump is read from GEONAMES_DIR.


```
locations-geocode.py ENTITIES.json OUT.json
```


A name is kept when GeoNames knows it as a place of a kind that fits the
entity type and the name is mentioned often enough (see MIN_MENTIONS).
Of several places with the same name the best known wins: scored by the
number of alternate names (names in other languages) and the inhabitants
(sqrt(alternates) * log10(population)); a place whose own name is the name,
and a country, counts triple, a town 1.5 times, a
county or district half, and the countries Adam lived in or talks about
most (US, GB, NL, BE) 1.2 times. Whisper's
spellings are merged first (Gilford -> Guildford), names that are not
places (STOP) and lowercase words are left for the hand list.

Altitude: GeoNames' elevation, else its DEM value (SRTM3 / GTOPO30), in
metres; none for countries, states and other areas.


### locations-timeline.py

Where was each show recorded? Finds the location each show states and
writes the periods, which locations-build.py puts into the "at" lists of
yaml/locations.yaml. The episode yaml is filled from those by

```
update-episodes-from-locations.py.
```



```
locations-timeline.py GEOCODED.json TIMELINE.json [REPORT.tsv]
```


TIMELINE.json: periods, the found places used, the phrases that say so,
and "coming to you from ..." names nothing resolved (with show dates).

Per show date, the first match wins:
0. a "recorded" period set by hand in yaml/locations.yaml,
1. the show notes: "From The Curry Manor, Guildford, UK" (episode

```
 description),
```

2. the start of the transcript: "coming to you from ...", "live from ...",

```
 "I'm at the ...", "here in ...",
```

3. Adam's blog of that day or the day before (json/blog-posts.json, from

```
 blog-posts.py): "I'm in ...", "arrived in ...", "greetings from ...".
```

The names are those of the curated entries of yaml/locations.yaml
(location and aliases) and the places locations-geocode.py resolved; in a
phrase a residence, venue or vehicle wins over a town. From the transcript
a country or region does not count ("here in America"), and "I'm at ..."
only counts for curated places (callers say it too). Whisper's usual
spellings (Gilford, Curie Cottage, Curricondo, ...) are normalised first.
Shows that state nothing are taken to be recorded where the previous one
was (Adam travelled a lot, so these periods are an assumption). A show that
only says the country or continent ("here in the UK", "back in Europe")
confirms the carried place when it lies there; otherwise the show is put
at the country.

REPORT.tsv: date, location, how (notes / transcript / country / confirmed /
carried), the phrase.


### mp3-mend-crlf.py

Mend an mp3 that went through a text-mode transfer which turned CR LF
(0D 0A) into LF (0A): every frame that held a CR LF pair is one byte short,
so the frame chain breaks there.


```
mp3-mend-crlf.py DAMAGED.mp3 MENDED.mp3 [REPORT.json]
```


For each frame that is one byte short, a CR is put back in front of one of
its LFs. The candidates are tried in order and scored by decoding the frame
with the frames before and after it (ffmpeg): decoder errors first, then the
loudness jump against the neighbouring frames (a wrong position garbles the
Huffman data into a noise burst). Frames that cannot be mended are replaced
by a silent frame of the same size, so the timing stays. The input is only
read.


### opml-from-html.py

-*- coding: utf-8 -*-


### release-audio-names.py

Release file names of the episode audio: DSC-YYYY-MM-DD.ext, the date being
the show date (locations-timeline.py showDate). Only when two episodes share
a day does the other one get a text to tell them apart (DISAMBIGUATE).
Writes ../yaml/release-audio.yaml (episode -> source file, release name,
size). The archive is not touched; the release copies get these names.


### srt-fix-names.py

Whisper's mishearings of "Curry" in the transcripts: Adam's name, curry.com
and the Curry houses. Only unambiguous forms; "Kerry" alone stays (John
Kerry, 2004), as do Adam Carolla and the unclear "Adam Kree", "Adam Kirk".
Rewrites ../srt/YEAR/*.srt in place (cue text only), or lists with --dry-run.

Usage, from python/: srt-fix-names.py [--dry-run] [files...]


### srt-music.py

Replace the lyrics Whisper transcribed from songs with one "[ Music ]" cue
spanning the song.


```
srt-music.py analyse AUDIO CACHE.json   speech/music scores per window
srt-music.py apply SRT CACHE.json [OUT] rewrite the transcript
```


The scores come from the PANNs Cnn14 audio tagger (AudioSet labels) on 5 s
windows every 2.5 s. A window is music when Music > 0.5 and Speech < 0.1:
Adam talking over a music bed scores Speech 0.2 .. 0.5, a song 0.0 .. 0.05.
Runs of music windows of 20 s or more become a music segment. Cues whose
middle falls in a segment are dropped, except in the first and last 6 s:
Adam often talks over the start and end of a song ("coming to you from
..."), which the tagger can't tell from the song. One "[ Music ]" cue covers
the segment between the cues that are kept.

Needs torch, panns-inference (~/.cache/dsc-audio-venv). The audio is only
read (ffmpeg).


### srt-transcribe.py

Transcribe a show to SRT with faster-whisper (the other transcripts were made
with FastWhisper Base/Small in Speech Note).


```
srt-transcribe.py AUDIO OUT.srt [MODEL]
```


MODEL defaults to "small". Run srt-music.py on the result afterwards to
replace song lyrics with "[ Music ]". Needs faster-whisper
(~/.cache/dsc-audio-venv). The audio is only read.


### stage-release.py

Build the upload stage (stage: of ../yaml/upload.yaml) from the archive and
the repo, flat folders as on the host (2026-10-28: /audio /chapters /opml
/srt /video /vtt), under the release names of ../yaml/release-audio.yaml:


```
audio/<release>.mp3      the audio copied as is, every old tag dropped
                         (ID3v1, ID3v2, APE, embedded images, ID3
                         chapters) and new ID3v2.4 tags written from the
                         episode: title, artist Adam Curry, track the
                         episode number (none for bonus items), album the
                         show, date the episode's, genre Podcast, and
                         artwork/episode-300x300.png as the only picture
                         (front cover). Old tags inside the audio (an inner
                         ID3v2 tag with show notes and art in #542, #678;
                         a trailing ID3v1) are cut out of the input
                         first (cleanSource). Plus an ID3v1 tag for old players:
                         title, artist, year, genre Podcast (186), Latin-1
                         cut to 30 characters; no track (v1 holds 1-255),
                         no album, no comment.
                         Checked file by file (verifyMP3): audio packets
                         identical to the source (MD5; less the old tags),
                         no old tag anywhere in the file,
                         the tag read back as v2.4 with exactly those
                         frames, the picture byte for byte, no APE tag,
                         the ID3v1 exactly as written, ffprobe reads it cleanly with the
                         source's codec and sample rate, and the header's
                         length is the length of the packets. A copy
                         that fails is thrown away and listed.
video/<release>.m4v|mp4  copied as is
srt/<release stem>.srt, vtt/<release stem>.vtt   copies of srt/YEAR/, vtt/YEAR/
chapters/<release stem>.json                     copies of chapters/YEAR/
opml/<name>.opml                                 copies of shownotes/YEAR/
```


Artwork goes up straight from the repo, the feed is not staged until it is
rendered. The archive is only read: nothing is ever written into it or into
the repo's mp3/ (refused), the stage gets real copies, never links. A file
already staged, newer than its source and the picture, and with the tags it
should have, is kept.
Files in the stage that belong to nothing are listed, and removed with
--prune.

Usage, from python/: stage-release.py [--write] [--prune] [PART...]

```
PART: media, srt, vtt, chapters, opml (all when none is named); without
--write only says what it would do
```


### update-episodes-dates.py

Every pubDate of the episode yaml (the item's, and the copies under itunes
and podcast) written as a valid RSS date, RFC 822 with a four digit year:
"Wed, 01 Sep 2004 19:52:26 +0000", the offset as stated. Reads the RFC form
and the older "Wed Sep  1 19:52:26 2004 +0000". Checks that the weekday
given fits the date, and stops on a value it cannot read (nothing is
guessed).

Usage, from python/: update-episodes-dates.py [--write]


### update-episodes-enclosures.py

Points every episode at its re-released audio: enclosure url
feed: audio_url, or video_url for a video (the OP3 prefix + host + folder),
+ the release name of ../yaml/release-audio.yaml, and one
alternateEnclosure, the same file, titled "DSC #356" ("DSC Bonus <date>").
The original url is kept as fileinfo: origin_url. Other alternates (files
we do not have) are dropped and listed. Lengths are the sizes of the release
copies in the stage (stage: of ../yaml/upload.yaml, made by

```
stage-release.py: images stripped, logo embedded), the source sizes where
```

a release is not staged yet.

Usage, from python/: update-episodes-enclosures.py [--write]


### update-episodes-from-audio.py

-*- coding: utf-8 -*-


### update-episodes-from-extracts.py

Fill placeholder link, guid, pubDate, enclosure url and description of the
episodes from the feed items update-episodes-from-rss.py extracted to
rss/episodes/*.yaml.

Only placeholders are replaced, curated values are kept. The extracts are
numbered by feed order, not by show, so they are matched to the episodes:

1. by the archive file's own tags (json/dsc-archive-tag-enclosures.json,

```
 from archive-tag-enclosures.py): the post embedded in the tags names the
 published mp3. Used when exactly one feed item is named and the number
 in the file's title tag, else the item's stated number or title date,
 agrees with the episode. This match also replaces
 values an earlier run took from another feed item.
```

2. by the number the item states ("#670 Daily Source Code for …"), when the

```
 item was published within 3 days of the show.
```

3. by date: the date in the enclosure url is the date of exactly one

```
 episode's audio file and no other extract carries that date.
```

4. by title date: items uploaded a day before or after the recording carry

```
 the upload day in the enclosure url, the item title has the show date.
```

5. by the archive file's tags again, for an episode left without any feed

```
 item, when nothing else matched the named item (logged).
```


Enclosure lengths stay the archive size: later published files were
re-tagged and differ in size from the archive copies.


### update-episodes-from-locations.py

Fills podcast:location and podcast:person of every episode yaml from
yaml/locations.yaml (the recording location of the show date, from the
"recorded" and "at" periods) and yaml/persons.yaml (Adam on every episode,
the others on the episodes listed with them).


```
update-episodes-from-locations.py [--write]
```


Location: rel "creator" (where the show was made), geo as a geo: URI, osm as
type letter and id, country as ISO 3166-1 alpha-2, name "Location, Town, CC".
A location without coordinates gets the name only.


### update-episodes-from-posts.py

Fill placeholder link, guid, pubDate, enclosure url and description of the
episodes from the original Daily Source Code posts in json/dsc-posts-*.json
(saved feed items, Wayback day pages where no feed has the post).

Only placeholders are replaced, curated values are kept. An episode is only
filled when exactly one episode yaml holds that show and its title date
agrees with its audio file.


### update-episodes-from-tags.py

Fill the enclosure url, link, guid and pubDate of episodes that no saved
feed item matches, from the tags of their archive file
(json/dsc-archive-tag-enclosures.json, from archive-tag-enclosures.py).

- enclosure url: the "Direct link to the show" of the post in the tags,

```
when the file names exactly one published mp3.
```

- link and guid: TGID, when it is a radio.weblogs.com permalink (the guid of

```
the Radio feed, 2006-2007). From 2009 TGID is the mp3 url, not the guid of
the Mevio feed, and is left out.
```

- pubDate: TDRL / TDR (release time), when the episode has a date only.

Only placeholders are replaced. The archive is only read (ffprobe).


### update-episodes-links.py

Sets the links of every episode to the files on the host (feed: base_url of
../yaml/daily-source-code.yaml), by release name (../yaml/release-audio.yaml),
folder structure of 2026-10-28 (/audio /chapters /opml /srt /video /vtt):


```
podcast:transcript  /vtt/<release stem>.vtt (text/vtt) and
                    /srt/<release stem>.srt (application/x-subrip), language
                    en, for the episodes with a transcript, else none
podcast:chapters    /chapters/<release stem>.json, where chapters/YEAR/ has
                    the file, else none
itunes:image        /artwork/episode-300x300.png
podcast:image       the same, purpose artwork (podcast:images is deprecated
                    and dropped)
```


Written as lists, the shape build.py renders. podcast:socialInteract is
dropped: the episodes have no comment threads (decided 2026-10-28).

Usage, from python/: update-episodes-links.py [--write]


### update-episodes-summaries.py

Plain text summaries: itunes:summary (and podcast summary where an episode
has one) of every episode become text, no HTML. Where the show has show
notes (shownotes/YEAR/<release stem>.opml) the summary is rendered from the
outline (one line per node, children indented with "- "), after the post's
own text when that is short and not part of the notes. Otherwise it is the
post's text with the markup taken out.

Links keep their text, except links to the media or the notes themselves
("mp3", "html", "opml"): the files are gone and the words mean nothing
without them; so do the lines left with only a size or a length ("20 mb,
17 minutes", "Production notes in"). Radio's outline rules (<rules> ...)
and empty nodes are left out. The description is not touched (raw show
notes).

Usage, from python/: update-episodes-summaries.py [--write] [EPISODE...]


### update-episodes-text.py

Cleans the text of every episode yaml: non-printable characters (control
characters, tabs, no-break spaces, line/paragraph separators) become a
space, runs of spaces become one, trailing spaces go. Line breaks stay
(CR LF and lone CR become LF), and so does the indentation at the start of
a line (the nesting of the show notes in the summaries). Invisible
characters inside words (soft hyphen, zero width space/joiners, BOM) are
removed, not spaced, so words stay whole.

The stub generator wrote a literal "\n" (backslash, n) before the closing
"Duration: HH:MM:SS" of the descriptions: a line break where text comes
before it, trimmed where nothing does.

Run it last, after the scripts that write episode text.

Usage, from python/: update-episodes-text.py [--write]


### upload.py

Upload to the S3 bucket behind thedailysourcecode.com with rclone, folder by
folder as ../yaml/upload.yaml lays it out, each file type with its own
Content-Type and Cache-Control.

A dry run unless --go: rclone lists what it would upload. Only copies:
nothing in the bucket is deleted. The bucket sits behind deep caches, so a
file once up is never overwritten (--ignore-existing): only the feed (manual)
is replaced; --replace overrides that for a deliberate fix (then have the
CDN invalidated). Folders go up in upload.yaml's order (media first, the
feed last), and the feed only when the bucket holds everything else (sizes
as staged), so nothing links to a file that is not there yet. Refuses names
that are not url-safe. A folder marked manual (the feed) goes up only when
named.

Usage, from python/: upload.py [--go] [--replace] [--remote R] [--stage DIR] NAME...

```
NAME     a name of upload.yaml (audio, video, chapters, srt, vtt, opml,
         artwork, feed), 'all' (every one but the manual ones: not the feed), or
         'check' (compare with the bucket by size, nothing uploaded)
--remote / --stage override upload.yaml's remote and stage
```

Environment: DSC_ACL=public-read if the bucket wants a per-object ACL (unset
when a bucket policy makes it public); DSC_TRANSFERS (default 4).
