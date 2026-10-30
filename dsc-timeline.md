# DSC Time line - Daily Source Code - Delta Sierra Charlie

This is a data source as much as a reference document, to establish a time line. An attempt at restoring the scattered pieces available across the internet into a fully functional RSS feed so that it can be played and listened to from first to last episode effortless.

The podcast feed was titled "Adam Curry: *Daily Source Code*" and the first episode was released August 14, 2004 and ran to November 30, 2013 when the latest and last episode were released.



## Background

Adam Curry have mentioned a few times both in chats on [podcastindex.social](https://podcastindex.social/) (Mastodon instance for the PodcastIndex.org - Podcasting 2.0 project) and in the podcast Podcasting 2.0, that he'd like to see the podcast restored and listenable again.


```text
The History of Podcasting

The true godfathers of podcasting are Dave Winer and Adam Curry. Dave Winer (http://scripting.com) is a software developer and RSS evangelist; he developed the popular weblog package Radio Userland (http://userland.com). Today, Dave “produces” the popular podcast Morning Coffee Notes (http://morningcoffeenotes.com). Adam Curry produces the ever-popular Daily Source Code (http://live.curry.com). Adam is well-known as amid-1980s former MTV VJ (see http://live.curry.com).

Citeted from "Podcasting - The Do-It-Yourself Guide", Todd Cochrane, page 8, printed in 2005.
```



## Present day

Christopher Isene started out on with just bits and pieces of what was available of the original feed that had been archived both on [radio-weblogs.com](http://radio-weblogs.com/0001014/categories/dailySourceCode/rss.xml) where is lived in it's first incarnation. Piecing together the beginning, [http://radio-weblogs.com/0001014/rss.xml](http://radio-weblogs.com/0001014/rss.xml) and [https://radio-weblogs.com/0001014/categories/dailySourceCode/rss.xml](https://radio-weblogs.com/0001014/categories/dailySourceCode/rss.xml) were used as source for the tail-end of the RSS feed, containing the last published episodes.







The first stumbling steps to searching further came with the BitTorrent Sync key from Adam's blog post [The Daily Source Code Archive Project](http://blog.curry.com/2014/01/15/theDailySourceCodeArchiveProject.html) of 2014-01-15, a few weeks after the last episode. The day before he had [tweeted](https://x.com/adamcurry/status/422938197006749696): "Looking for a full archive of 'Daily Source Code' mp3s". For a number of "[stupid and careless] reasons" Adam no longer had most of the mp3s, and he started a BitTorrent Sync archive to collect them from listeners around the world, with the read key `B5XIHOVFXGSA2QXS7ED6ONN4KG5JTH6T6`. In an update to the post, "Super Friend of the show Raymond Poort is uploading the entire archive as we speak!"

The audio of this restoration came from that BitTorrent Sync archive, in December 2022. From there the search went on to the RSS: the old feeds on radio-weblogs.com, PodShow and Mevio, and their archived copies. Along the way Adam's original iPod script turned up, an AppleScript compiled with its source stripped out, which was reverse-engineered with help from others. The rest is history.





Also found mirrored online:

* [https://johntrain.org/nextcloud/s/nPY4sg3dJZaq5yk](https://johntrain.org/nextcloud/s/nPY4sg3dJZaq5yk)

* [https://archive.org/details/pcs_The_Daily_Source_Code](https://archive.org/details/pcs_The_Daily_Source_Code)


Some episode info:

https://web.archive.org/web/20130922024941/http://dailysourcecode.mevio.com/#show-episodes


Mirrored RSS: [https://web.archive.org/web/20061116220024/http://www.btpodshow.com/feeds/dailysourcecode.xml](https://web.archive.org/web/20061116220024/http://www.btpodshow.com/feeds/dailysourcecode.xml)


Search Start: [Daily Source Code Adam Curry](https://web.archive.org/web/20240000000000*/Daily%20Source%20Code%20Adam%20Curry)






### Restoration time line

* 2014-01-14 - Adam [tweets](https://x.com/adamcurry/status/422938197006749696): "Looking for a full archive of 'Daily Source Code' mp3s".
* 2014-01-15 - Adam starts [The Daily Source Code Archive Project](http://blog.curry.com/2014/01/15/theDailySourceCodeArchiveProject.html), a BitTorrent Sync archive to collect the mp3s; Raymond Poort uploads the entire archive.
* 2022-12 - The audio archive is fetched from the BitTorrent Sync archive of 2014.
* 2022-12-22 - The project starts: first commit of this repository.
* 2022-12-23 - First rendition of a restored DSC RSS feed.
* 2026-10-29 - The restored feed goes live at [https://thedailysourcecode.com/rss.xml](https://thedailysourcecode.com/rss.xml), Adam's domain: 863 numbered episodes and 58 bonus items, with transcripts and chapters for all 921, after 251 commits.
* 2026-10-29 - Dave Jones adds the show to Podcast Index by hand as feedId 2004, the year the show started: [https://podcastindex.org/podcast/2004](https://podcastindex.org/podcast/2004).

Almost four years from the first commit to the live feed, and almost thirteen from Adam's call for the archive.


[[_TOC_]]

---

## Episode distribution over years

| Year | From |  To | Episodes |
| ---- | ---: | --: | -------: |
| 2004 |  001 | 096 |       96 |
| 2005 |  097 | 306 |      210 |
| 2006 |  307 | 521 |      215 |
| 2007 |  522 | 704 |      181 |
| 2008 |  705 | 813 |      109 |
| 2009 |  814 | 821 |        8 |
| 2010 |  822 | 855 |       34 |
| 2011 |  857 | 863 |        6 |
| 2012 |  864 | 866 |        3 |
| 2013 |  867 | 867 |        1 |

863 episodes, numbered 001 to 867. Adam skipped four numbers, so there is no data or audio for them and they have no episode: #687 and #688 (the feeds go #686, 2007-11-16, to #689, 2007-11-19), #856 (#855, 2010-12-17, to #857, 2011-01-06) and #859 (#858, 2011-01-17, to #860, 2011-02-05).

---

## Curiosa

Counted over the 863 numbered episodes, from the release audio.

**Listening time**: 43,401 minutes, 723 hours, a bit over 30 days without a
break. The average episode runs 50 minutes.

| Year | Episodes | Minutes | Hours | Average (min) |
| ---- | -------: | ------: | ----: | ------------: |
| 2004 |       96 |   3,409 |  56.8 |          35.5 |
| 2005 |      210 |   8,908 | 148.5 |          42.4 |
| 2006 |      215 |   9,664 | 161.1 |          45.0 |
| 2007 |      181 |   7,908 | 131.8 |          43.7 |
| 2008 |      109 |   6,551 | 109.2 |          60.1 |
| 2009 |        8 |     597 |  10.0 |          74.7 |
| 2010 |       34 |   4,780 |  79.7 |         140.6 |
| 2011 |        6 |   1,051 |  17.5 |         175.1 |
| 2012 |        3 |     447 |   7.4 |         149.0 |
| 2013 |        1 |      86 |   1.4 |          85.8 |

Fewer shows, longer shows: from 2010 the episodes run two to four hours.

**Longest**: #852 (2010-11-19) 3 h 49 min, #854 (2010-12-04) 3 h 40 min,
#860 (2011-02-05) 3 h 32 min.
**Shortest**: #010 (2004-08-22, a test) 18 seconds, #051 (2004-10-22, the
iPodder video) 36 seconds, #061 (2004-11-04) 1 minute.

**Recording day**: Friday (187), then Monday (165), Wednesday (156), Tuesday
(154), Thursday (150), Saturday (31) and Sunday (20). Only 6% of the shows
were recorded on a weekend.

**Release day**: Friday again (174), then Monday (162), Wednesday (159),
Thursday (148), Tuesday (146), Saturday (43), Sunday (30). 89% went out the
same day they were recorded, almost all of the rest the next day. Most were
published between 12:00 and 17:00 UTC: early afternoon in Europe, morning on
the US East Coast.

**Busiest month**: August 2006, 22 episodes; September 2004, January 2006
and March 2006 had 21 each.

**Longest run of daily shows**: 7 days, the first week (2004-08-13 to
2004-08-19).

**Longest silences**: 455 days before the last episode (2012-08-29 to
2013-11-27), 396 days in 2009-2010 (2009-02-16 to 2010-03-19) and 349 days in
2011-2012 (2011-05-13 to 2012-04-26).

### DSC top lists

From the songs listed in the show notes: 1045 plays in 370 episodes, mostly 2006-2008 when every show note had a "Music in this episode" list. Earlier shows list their music less often, so the podsafe years of 2005 count for less than they should. A song counts once per episode it is listed in.

**Most played song**: Pete Hopkins - Become, in 6 episodes (#536 to #767).

**Most played artist**: The Fire Apes, in 12 episodes; then Geoff Smith (11) and Black Lab (10).



Songs played in three or more episodes:

|   # | Song                                      | Episodes | Played in                      |
| --: | ----------------------------------------- | -------: | ------------------------------ |
|   1 | Pete Hopkins - Become                     |        6 | #536, #545, #554, #565, #624 … |
|   2 | Kevin Reeves - Throw me a line            |        5 | #435, #437, #445, #470, #560   |
|   3 | The Shakes - Liberty Jones                |        5 | #435, #438, #460, #477, #492   |
|   4 | Andy Stone - In the Coffee Shop, When     |        3 | #519, #552, #626               |
|   5 | Bob Gentry - Upside Down                  |        3 | #337, #489, #618               |
|   6 | Cherry Suede - Not A Day Goes By          |        3 | #505, #546, #709               |
|   7 | Howard Jones - Building Our Own Future    |        3 | #483, #486, #494               |
|   8 | Junior - What Was I Thinking              |        3 | #594, #597, #645               |
|   9 | Laura Lambert - Am I Wrong For Loving You |        3 | #539, #546, #555               |
|  10 | The Fire Apes - Let Me Know               |        3 | #588, #589, #672               |



Top 20 artists, by the number of episodes they were played in:

|   # | Artist         | Episodes | Played in                      |
| --: | -------------- | -------: | ------------------------------ |
|   1 | The Fire Apes  |       12 | #461, #473, #491, #588, #589 … |
|   2 | Geoff Smith    |       11 | #409, #422, #478, #504, #509 … |
|   3 | Black Lab      |       10 | #438, #444, #498, #508, #558 … |
|   4 | The Shakes     |       10 | #435, #438, #460, #477, #492 … |
|   5 | Matthew Ebel   |        8 | #487, #548, #590, #626, #666 … |
|   6 | Munk           |        8 | #422, #463, #523, #539, #637 … |
|   7 | David Ippolito |        7 | #414, #435, #440, #450, #601 … |
|   8 | Kevin Reeves   |        7 | #435, #437, #445, #470, #523 … |
|   9 | Pete Hopkins   |        7 | #536, #540, #545, #554, #565 … |
|  10 | Howard Jones   |        6 | #483, #486, #494, #523, #623 … |
|  11 | Party Ben      |        6 | #631, #660, #692, #724, #726 … |
|  12 | Brother Love   |        5 | #196, #220, #497, #568, #595   |
|  13 | Wylde Bunch    |        5 | #466, #467, #474, #523, #671   |
|  14 | Blake Morgan   |        4 | #562, #651, #655, #673         |
|  15 | Bob Gentry     |        4 | #337, #489, #510, #618         |
|  16 | David Bowie    |        4 | #549, #737, #798, #832         |
|  17 | David Usher    |        4 | #650, #655, #681, #707         |
|  18 | DJ Earworm     |        4 | #141, #601, #630, #649         |
|  19 | DJ Moule       |        4 | #604, #693, #705, #828         |
|  20 | Girls Stuff    |        4 | #481, #493, #649, #710         |

Also in 4 episodes: Jimmie Bratcher, Kelly Brock, Lascivious Biddies, Michael Jackson, Panic At The Disco, Sophia Ramos, The Alice Project, The Beatles.

### Guests

The DSC was mostly Adam alone, with the voicemail line and listener audio
doing the rest. The feed names 16 people besides Adam (`podcast:person`),
on the items they hosted, co-hosted, produced or were the guest of:

| Person            | Role          | Episodes                                                                                            |
| ----------------- | ------------- | --------------------------------------------------------------------------------------------------- |
| Patricia Paay     | co-host, host | #137; #142; #172; Recht Voor Z'n Raap Podcast #2                                                    |
| Andrew Grumet     | guest         | DevCast 4; DevCast 5; DevCast 6                                                                     |
| Dave Winer        | co-host       | Trade Secrets: voip setups sux; Trade Secrets: xten sipcall and 'leakage'; Dave and Adam Phone Test |
| Kevin Ostrowski   | guest         | DevCast002; DevCast 5                                                                               |
| Marcus Couch      | producer      | #866; DSC-BOC-2007-01-01                                                                            |
| Anji Bee          | producer      | Best of Charlie #5                                                                                  |
| Barbara Couch     | producer      | DSC-BOC-2007-01-01                                                                                  |
| Bobbi Eden        | guest         | DSC-Special Report with Bobbi Eden                                                                  |
| Chris Doelle      | producer      | DSC-BOC5-2007-01-05                                                                                 |
| Dawn Miceli       | host          | The Dawn and Drew Show #646                                                                         |
| Drew Domkus       | host          | The Dawn and Drew Show #646                                                                         |
| Erin O'Neill      | guest         | DevCast 3                                                                                           |
| Happy             | producer      | DSC-BOC4-2007-01-04                                                                                 |
| Joep Berkenbosch  | guest         | #838                                                                                                |
| Leo Laporte       | host          | TWiT 85: The Podfather                                                                              |
| Sander Hoksbergen | producer      | DSC-BOC3-2007-01-03                                                                                 |

**Most frequent guest**: The Lady Patricia (Patricia Paay, Adam's wife at the
time), on the show in at least 27 episodes; #137 and #142 were her
shows, #172 (RVZR) she co-hosted:
#073, #081, #137, #142, #172, #272, #282, #334, #413, #434, #437, #438, #443, #447, #451, #455, #459, #462, #470, #493, #516, #546, #565, #597, #623, #704, #748.

**Christina**, Adam's daughter, joins in at least 7: #135, #157, #282, #412, #451, #498, #648.

**Most frequent contributor**: Jan Polet, with his weekly HitTest of new
music, in 46 episodes: #131, #133, #144, #167, #169, #170, #175, #191, #195, #203, #215, #229, #230, #231, #232, #233, #234, #237, #240, #484, #488, #497, #602, #612, #615, #619, #622, #626, #631, #642, #655, #663, #669, #675, #678, #691, #698, #700, #703, #708, #730, #732, #733, #745, #755, #756.

These counts are from the show notes, so they are lower bounds: a guest who
isn't in the notes isn't counted.

## Locations

Where the shows were recorded, from `yaml/locations.yaml`: the first and last
show stated or carried there, the number of shows and of separate periods
(Adam travelled between Europe and the US, so the periods interleave).

| Caption       | Location          | Latitude | Longitude | From       | To         | Shows | Periods |
| ------------- | ----------------- | -------: | --------: | ---------- | ---------- | ----: | ------: |
| Curry Castle  | Rijkevoorsel, BE  |  51.3308 |    4.7662 | 2004-08-16 | 2004-11-17 |    40 |       7 |
| Curry Bunker  | Amsterdam, NL     |  52.3656 |    4.8918 | 2004-08-18 | 2004-11-03 |     9 |       5 |
| Curry Cottage | Guildford, UK     |  51.2396 |   -0.5458 | 2004-11-20 | 2007-01-29 |   294 |      37 |
| Miami         | Miami, US         |  25.7743 |  -80.1937 | 2005-01-04 | 2005-01-04 |     1 |       1 |
| Curry Condo   | San Francisco, US |  37.7749 | -122.4194 | 2005-09-15 | 2008-10-11 |   138 |      27 |
| Curry Manor   | Guildford, UK     |  51.2354 |   -0.5743 | 2007-01-16 | 2008-12-31 |   208 |      23 |
| Curry Coast   | Fire Island, US   |  40.6949 |  -72.9792 | 2007-08-16 | 2007-08-20 |     2 |       1 |
| Curry Terrace | London, UK        |  51.5085 |   -0.1257 | 2009-01-07 | 2010-03-19 |     9 |       1 |

Trips, hotels, studios and vehicles are in `yaml/locations.yaml`; the
episodes get their `podcast:location` from there.

---

## Episodes of note

* Episode 001 (2004-08-13) - The first episode, explainer and thoughts.
* Episode 180 (2005-05-20) - The episode demonstrated on stage during introduction of [Steve Jobs previews podcasting All Things D3 2005](https://www.youtube.com/watch?v=B8WCRXCdDz4&t=1015s) with ([Steve Jobs](https://en.wikipedia.org/wiki/Steve_Jobs), [Kara Swisher](https://en.wikipedia.org/wiki/Kara_Swisher) and [Walt Mossberg](https://en.wikipedia.org/wiki/Walt_Mossberg)) where Adam dropped a series of profanities in general and about Apple's product in particular.
* Episode 863 (2011-05-13) - The 'FUBAR Friday BitCoin Blast Off' got very popular among Bitcoin, crypto-bros
* Episode 867 (2013-11-27) - The last episode
