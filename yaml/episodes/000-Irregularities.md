# Episodes - Irregularities

Found while cross checking episode yaml, RSS fragments (`rss/`), transcripts (`srt/`), the timeline (`dsc-timeline.md`) and the audio archive (`/media/chrise/work/audio/dsc/DSC`, read only). To be checked later.

Status: `[ ]` open, `[x]` resolved.



## Numbering

- [x] **Renumbering applied 2026-10-26**: `001`-`179` as proven below, `180`-`199` moved up 10, and the fixes above #200 (`222`/`225`, `362`/`363`, `749`/`750`, `755`/`756`). 33 new episodes built from archive audio and the original posts (6 missing shows, the 18 s test clip, the 8 other audio posts in the feed, and `222` `362` `488` `558` `621` `750` `756` `821`). 863 of 867 episodes now have audio; the other 4 are the skipped numbers. Old → new table: [`000-Renumbering-2026-10-26.md`](000-Renumbering-2026-10-26.md). **Episode numbers in the items below are the old numbers** unless they say otherwise.
- [ ] **Two shows tagged #813**: `2008/DSC-2008-12-28.mp3` ("#813 … Sunday December 28th 2008", not in any episode) and `2008/DSC-2008-12-31.mp3` ("#813 DSC Year End Special", episode `813`; the lookup calls it `813.5`). Decide how to number the 12-28 show.
- [ ] No transcript yet for 10 of the new episodes: `032` `051` `052` `137` `142` `168` `172` `179` `621` (video) `821`.
- [ ] `032` (Trade Secrets 2004-09-22): the recovered copy is partial, 8.2 of the published 60.1 MB, decodes to 10:55.
- [ ] `750` / `756`: the archive files are misnamed (`DSC-2008-04-25.mp3` is DSC-750 of 2008-04-23, its tag title copies #749's; `DSC-2008-05-07-1.mp3` is DSC-756 of 2008-05-09). Episode titles and dates follow the feed items.
- [x] `update-episodes-from-audio.py`: an exact enclosure length no longer takes a file another episode holds. The 2004-09-20 item was published with 2004-09-19's length (29880248), which would have moved `030` onto the 09-19 file.

- [ ] **Adam renumbered on 2005-05-20.** Before that no episode carries a number. 2005-05-18 is announced as "show number 250" (*"I haven't counted. Let's say this is show number 250"*), 2005-05-20 as *"officially show number 180 … as calculated by the people who track … I have lost count so long ago"*. From #180 the stated numbers (RSS titles, transcripts) run unbroken to #866 (2012-08-29).
- [ ] Episodes `170`-`189` (mp3 2005-05-20 .. 2005-06-24) are officially #180-#199, our numbering is 10 low in that range. From `200` (2005-06-25, Gnomedex 5.0 keynote, *"It's actually number 200"*) numbering agrees with the official numbers.
- [ ] Episodes `190`-`199` are old format stubs without mp3, dated 2005-06-25 .. 2005-07-15, overlapping 200-209. They look like filler bridging the jump. `196` holds the shownotes of 2005-06-17 (official #196, our `186`).
- [x] **No numbering gap, the yaml is missing shows instead.** Proven from Wayback: every distinct audio enclosure posted in the Daily Source Code category before the #180 post counts to exactly **179** (171 DSC shows + 8 other audio posts in the same feed: Trade Secrets, DSC Commercial, no source 2day, Patricia Paay I and II, Podshow Strategy Cast 2.0, Recht Voor Z'n Raap, Podshow on Sirius). Radio UserLand item numbers run unbroken from #6980 (2004-12-20) to #7072 (the #180 post), and before that the month calendars on the Wayback day pages account for every day. Full list, sources and the mapping to current yaml: [`000-Numbering-before-180.md`](000-Numbering-before-180.md).
- [ ] Apply the proposed numbering `001`-`179` from `000-Numbering-before-180.md` (not applied). Decide whether the 8 other audio posts get yaml or stay numbered gaps.
- [ ] Shows with no episode yaml: 2004-09-02, 2004-11-04, 2004-11-10, 2004-11-17, 2005-03-02, 2005-03-03. Empty stubs `059` and `063` sit exactly at 2004-11-02 (#59) and 2004-11-09 (#63). 2004-08-26 was not missing, it is `013` (see `010`-`013` below).
- [ ] Two yaml for one show: `014`/`015` (2004-08-27), `018`/`019` (2004-09-03), `130`/`146` (2005-03-31). `129` is titled 2005-03-02 but carries the 2005-03-25 mp3, `143` is an empty stub for 2005-03-25.
- [x] 2005-03-29 is not a separate show. Post #7044 "Daily Source Code for March 29th 2005" published a broken enclosure (`DSC-2005-03-29.mp3`, `text/html`, 12444 bytes). The show is `DSC-2005-03-30.mp3` ("Quick update from Curry Condo"), held by `145`. Empty stub `144` (2005-03-29) is that broken link.
- [x] The second post of 2004-08-22 (21:14 CEST) is an 18 s clip, `DSC-2004-08-22 test.mp3` (feed length 125567). It counts as one of the 179.
- [x] Empty days before #180 are settled. The Wayback month calendars show no DSC post on any empty day except 2004-08-31, 2004-10-31, 2004-11-30 and 2005-04-30 (month ends, no later page that month). Adam confirms no show on 2004-09-30 (*"I missed the show yesterday"*, 2004-10-01) and 2004-10-19 (*"I missed the source code, I wasn't able to tape"*, 2004-10-20). No RSS hunting is needed for numbering before #180. RSS copies would still add titles and show notes for the 38 shows known only as audio.
- [ ] **2006-03-29 (#362) has no episode yaml.** Post #7286 "#362 Daily Source Code for Wednesday March 29th 2006" and post #7287 "#363 … Thursday March 30th 2006" settle it. The archive has `2006/DSC-2006-03-29.mp3` (unused), `362` holds the 2006-03-30 show (#363) and `363` is an empty stub. Move `362` to `363` and build `362` from the 03-29 mp3 and post #7286 (in `json/dsc-posts-2005-2007.json`).
- [x] Stated numbers in post titles agree with the episode yaml for every numbered post found (#316-#398 in 2006, #563 and #564 in 2007), except the known `170`-`189` = #180-#199 and `362` above.
- [ ] `yaml/episode-lookup.yaml` drifts from the mp3 dates from 2004-08-23 on, up to ~2 months in 2005 (e.g. `110` = 2005-02-14, mp3 is 2005-02-01; `180` = 2005-06-25). It numbered the extracted fragments in `rss/episodes/`, so 85 fragments sit under the wrong episode number.
- [x] `010`-`013`: the fragments were right, the audio files were one show early. The enclosure lengths match the archive byte for byte (`DSC-2004-08-23.mp3` .. `DSC-2004-08-26.mp3`) and the corrected durations agree with Adam's notes ("15 minutes" 00:15:37, "17 minutes" 00:17:35, "24 minutes" 00:24:39). Fixed by `update-episodes-from-audio.py`, which now prefers an exact enclosure length match over `fileinfo.filename`. From `014` on, enclosure and file agree.
- [x] `687`, `688`, `856`, `859` are skipped numbers, not lost shows: the original feeds go #686 (2007-11-16) → #689 (2007-11-19), and `rss/dailysourcecode-2011-02-04.xml` / `-2012-04-05.xml` list DSC-855 (2010-12-17), 857 (2011-01-06), 858 (2011-01-17), 860 (2011-02-05); the archive mp3 tags agree and has no file between. Decide whether the stubs stay as numbered gaps or go.
- [ ] `yaml/episode-lookup.yaml` has an episode `813.5` (2008-12-31).
- [ ] mp3 `track` tags are not episode numbers before mid 2005 (day of month) and unreliable after, not used.
- [ ] Transcripts also carry spoken numbers in the jingle, e.g. "Delta Sierra Charlie 384" (2006-05-10), not harvested yet. Useful for the renumbering.



## Episodes pointing at the wrong mp3

A stub generator bug gave episodes dated `YYYY-MM-MM` (day equal to month) the mp3 of the last show of that month, so size, duration, title and date came from another episode. Fixed by `python/update-episodes-from-audio.py` where the right file exists in the archive, is unused and fits between the neighbours:

- [x] `023` 2004-09-09, `058` 2004-11-11, `111` 2005-02-02, `162` 2005-05-05, `179` 2005-06-06, `204` 2005-07-07, `221` 2005-08-08, `238` 2005-09-09, `257` 2005-10-10, `277` 2005-11-11, `296` 2005-12-12, `346` 2006-03-03, `381` 2006-05-05, `400` 2006-06-06, `437` 2006-08-08, `538` 2007-02-02, `576` 2007-04-04, `630` 2007-07-07, `699` 2007-12-12, `730` 2008-03-03, `743` 2008-04-04, `766` 2008-06-06, `781` 2008-08-08, `788` 2008-09-09

Not fixed, check by hand:

- [ ] `129` / `130`: `129` points at `DSC-2005-03-25.mp3`, `130` at `DSC-2005-03-31.mp3` (also used by `146`). The archive files `DSC-2005-03-02.mp3` and `DSC-2005-03-03.mp3` are not used by any episode.
- [ ] `014` / `015` both `DSC-2004-08-27.mp3`, `014` with a size (29582761) that matches no archive file. Archive `DSC-2004-08-26.mp3` is unused. Hand merged.
- [ ] `018` / `019` both `DSC-2004-09-03.mp3`, `018` with size 32195843 matching no archive file; `018` itunes title says "Thursday September 02nd 2004". Archive `DSC-2004-09-02.mp3` is unused. Hand merged.
- [ ] `009` / `010` both 2004-08-22: `010` points at `DSC-2004-08-22.old.mp3` (127615 bytes, not in the archive). Archive has `DSC-2004-08-22 test.mp3`. `010` got the fragment of 2004-08-23.



## Audio archive

- [ ] 2005-03-29 is missing: `2005/DSC-2005-03-29.mp3.txt` is a saved ".Mac member site not found" page. `2005/DSC-2005-03-30.mp3` is tagged track 29, possibly the 03-29 show under the wrong name (`144` has no file).
- [x] `2005/DSC-2005-07-14.mp3.txt` is truncated: its 15928 bytes are an exact prefix of `http://mp3.dailysourcecode.podshow.com/DSC-2005-07-14.mp3` on Wayback (captures 20060829213100 and 20120314144149, byte identical, 14691527 bytes, decodes to 00:30:30 without errors, tags `#208 DSC-2005-07-14`, "Daily Source Code for July 14th 2005 #208"). `208` now has size, duration and description from that file; `fileinfo.source` is the Wayback URL.
  - [ ] Recovered file saved as `mp3/2005/DSC-2005-07-14.mp3`, not copied into the archive (read-only). Place it there yourself and rerun `update-episodes-from-audio.py`, which then sets `fileinfo.source` back to the archive path.
- [x] `255` pointed at `DSC-255-2005-10-06-JobCast.mp3`. The category posts settle it: post #7159 "Daily Source Code for Thursday October 6th 2005 #255" has `DSC-255-2005-10-06.mp3` (49:05), "JobCast" is a post of its own, #7162 (`DSC-255-2005-10-06-JobCast.mp3`, 2:49). `255` now uses the archive `2005/DSC-2005-10-06.mp3`.
- [ ] `582` matched to `2007/DSC-2007-04-17-repost.mp3`, confirm it is the 2007-04-17 show.
- [ ] `818` matched to `2009/818 DSC-818-2009-01-2009.mp3` (date in name broken, tags say #818).
- [ ] `206` (`DSC-206B-2005-07-11.mp3`) and `770` (`DSC-770-2008-06-18.mp3`) matched to `DSC-2005-07-11.mp3` and `DSC-2008-06-18.mp3`.
- [ ] `Misc/` holds copies of 2005-01-07, 2005-01-10, 2005-01-19 and numbered copies of 259-262, 336 and 867; `Misc/DSC-2005-01-19.mp3` has the title `2DSC-005-01-19`.
- [x] Durations in the episode yaml were a few seconds off; now replaced by a full decode (e.g. `001` 1357 → 1350, `020` 2469 → 2466).
- [x] `2005/DSC-2005-10-02.mp3` is damaged: same size as `http://mp3.dailysourcecode.podshow.com/DSC-251-2005-10-02.mp3` on Wayback (capture 20120314150914, 46094223 bytes), but the archive copy is zero-filled from byte ~14.9 MB on (31170634 of 31170646 differing bytes are zeros in the archive), so it decodes to 00:20:12. The Wayback copy decodes to 01:04:00 without errors. `251` now has the full duration; `fileinfo.source` is the Wayback URL.
  - [ ] Recovered file saved as `mp3/2005/DSC-2005-10-02.mp3`, not copied into the archive (read-only). Replacing the archive copy is your call.
- [x] `2009/DSC-2009-01-07.mp3` and `2009/DSC-2009-01-09.mp3` are **not** damaged. Their header duration is too long (3696 s and 4290 s), but the decoded audio is bit-identical (PCM MD5) to the podshow files on Wayback (`media.podshow.com/media/21/episodes/138688/dailysourcecode-138688-01-07-2009_pshow_283479.mp3`, `…/138821/dailysourcecode-138821-01-08-2009_pshow_283673.mp3`, captures 2013-06-16/17, which have the same wrong header). The decoded length (01:00:09, 01:05:54) is right.
- [ ] `815`: file and title say 2009-01-09, the feed item is titled `DSC-815-2009-01-09` but its enclosure is `dailysourcecode-138821-01-08-2009.mp3`, pubDate `Thu, 08 Jan 2009 11:48:44 -0800`, and the mp3 tag title is `DSC-815-2009-01-07`. Which date is the episode date?
- [x] `homepage.mac.com/dailysourcecode/` on Wayback, all captures with status 200: 30 complete show mp3s from 2004-12 .. 2005-09. Each archive copy decodes without errors to the right length, so none were downloaded. The OPML there (ipodder directories, podSquad) is already in `opml/`. Only `DSC-2005-04-19.mp3` is missing from the archive; see below.
- [x] `curry.com/xml/rss.xml` on Wayback: 28 captures, 2001-07 .. 2008-05, saved in `rss/` (`curry-com-xml-rss-*.xml`); the 2005-07-17 capture was a "Server Maintenance" page. Manila's feed for curry.com: the DSC items carry no `pubDate`, their guids are curry.com permalinks (`http://www.curry.com/2005/07/28#a41850`), and the enclosures are the same as in the radio.weblogs feeds. Only two enclosures are new, neither a DSC show: No Agenda `NA-030-2008-05-10` and a Trucker Tom promo.
- [x] `dailysourcecode.com` on Wayback (212 captures) is the PodShow/Mevio show site: page backgrounds and banners, listener thumbnails, `/feed.xml` of 2007-10-20 (the same date as `rss/feed-2007-10-20.xml`), and 2008-09 .. 2009-02 player pages for single episodes. It holds nothing for the episodes still missing data.
- [ ] Episode artwork: the 2010-2011 items link per-episode art (for example `http://www.curryscloud.com/shownotes/dsc860Art.png`), and the Mevio items have `itunes:image`. Most of it is already in `img/`. For 2010 the art of `837` (07-02), `841` (08-13), `842` (08-18), `843` (08-21) and `844` (08-27) was missing, and the archive mp3s carry no embedded picture. Wayback has no capture of the full-size originals (`origin.psstatic.mevio.com` / `origin.psstatic.podshow.com/images/shows/21/episodes/<id>/large/`), only the 200x112 thumbnails of mevio's image proxy for 837, 841 and 844. Those are saved as `img/2010/DSC-2010-MM-DD-01-200x112.jpg`; they are candidates for upscaling. Nothing found for 842 and 843 (the img.mevio.com listing stops at 5000 captures, so not every capture was checked).
- [ ] Media on Wayback that the archive does not have, saved under `mp3/<host>/<original path>`:
  - `mp3/homepage.mac.com/dailysourcecode/DSC/DSC-2005-04-19.mp3`: tags `DSC-2005-04-19`, album "A quick update from Utrecht", 12:10 (decodes to 11:59 with "Header missing" errors, capture 2005-11-12). Not posted in the Daily Source Code category (#162 is 2005-04-18, #163 2005-04-21) and no archive file for that day: an unpublished or differently published show?
    - [x] The file went through a text-mode transfer: CR LF (`0D 0A`) became LF, so 480 frames are 1 byte short (2 pairs of `0D 0A` are left, where a clean file of this size has about 200). A mended copy is in `mp3/repaired/homepage.mac.com/dailysourcecode/DSC/DSC-2005-04-19.mp3`, made with `python/mp3-mend-crlf.py`; the report is next to it (`.mend.json`). In 422 frames the CR was put back in front of an LF. When a frame had more than one LF (314 frames), the position was chosen by decoding it with its neighbours (no decoder errors, no jump in loudness), so this is a best guess. 59 frames could not be mended and are silent (1.5 s in all): 51 of them have no LF at all, so a byte was lost some other way, and nearly any byte at any position decodes without errors, so there is nothing to go on. The mended copy decodes without errors to 12:10.14 (header 12:10.12).
    - [x] It has many short loud transients (26 a minute, the studio shows of that week have 1-4). They are in the damaged decode at the same rate, and they start at random points within a granule, while bitstream damage would start on granule boundaries. So they are in the recording (a field recording from Utrecht), not caused by the damage or the repair.
- [x] Decode scan of the whole archive (ffmpeg, 917 files): 71 files report errors. Most have a single cut-off frame at the end or a join of two recordings (`2007/DSC-2007-02-08.mp3` 42 errors from 12 joins, `2007/DSC-2007-10-29.mp3` 3 joins; many 2006 shows have 6-12 errors). Early 2004 files have an error in the first frame ("invalid new backstep"). In all of them the decoded length matches the header, so none is damaged beyond about 26 ms per error. The only real damage is `2005/DSC-2005-10-02.mp3` (see above).
  - Trade Secrets (Dave & Adam): `mp3/cloud2.urj.nl/gems/TS-2004-09-22.mp3` ("Twinkies & Netflix", post #32 in the numbering), `mp3/homepage.mac.com/adamcurry/TS/TS-2004-09-25.mp3` ("voip setups sux"), `TS-2004-09-28.mp3` ("xten sipcall and 'leakage'").
  - `mp3/homepage.mac.com/adamcurry/gems/ipodder.mp4` (the DSC Commercial, post #51), `mp3/homepage.mac.com/adamcurry/Default/podcastDefaultWelcome.mp3`, `mp3/homepage.mac.com/adamcurry/gems/to-adam-from-dawn.mp3` (Dawn and Drew, 2004).
  - 25 files from `mp3.dailysourcecode.podshow.com` in `mp3/mp3.dailysourcecode.podshow.com/`: segments played in #236-#238 (Katrina PSAs, promos, podsafe tracks, HitTest #57), `podshowXmas1-3.mp3`, `xmasPodshow4-5.mp3`, `DSC-VMC-1-2006-03-02.m4v` (DSC Video Music Podcast #1, post #7263), `MyDesktopVideoPodcast.mp4` (post #7282), `EGTF-EHRD-inflight.MP4`, `the_message.mp3.mpg`.
  - 17 original uploads from `adam.opml.org` (2004-11-13 .. 12-15, Wayback captures 2004-11/12) in `mp3/adam.opml.org/`. Each decodes to the same audio as the archive copy (PCM MD5), with no decode errors; only the tags differ (the archive copies were re-tagged later: iTunNORM, grouping). They are kept as the files as published. The 2004-11-11 capture was truncated (the first 24 minutes, identical to the archive) and was not kept.
  - Not saved: `static2.podcatch.com/blogs/gems/snedit/` (Dave Winer's).
- [ ] `018` had size 32195843 (another copy of the file?), now the size of the archive `DSC-2004-09-03.mp3`, 27984382, the same file as `019`.

### Archive files not used by any episode

Regular show dates (updated after the renumbering of 2026-10-26):

- [x] Now linked: 2004-08-26, 2004-09-02, 2004-11-02, 2004-11-04, 2004-11-09, 2004-11-10, 2004-11-17, 2005-03-02, 2005-03-03, 2005-04-21, 2005-05-06, 2005-08-13, 2005-10-06, 2006-03-29, 2006-10-31-1, 2007-03-07, 2007-06-19 (`.mp4`, #621 VIDEO), 2008-04-25 (#750), 2008-05-07-1 (#756), `821 It's Getting Hot In Here.mp3`, the 2005 PPP, Podshow20, RVZR-2005-06-08 and PSS-2005-05-19-2 files.
- [ ] Still unused: `2006/DSC-2006-05-06.mp3` ("DSC_Rewind_Week_Of_5-5-06", a weekly rewind), `2006/DSC-2006-03-20/21/22/25.m4v` (video versions?), `2008/DSC-2008-12-28.mp3` (the second #813, see Numbering).

Specials and extra parts, decide whether they belong in the feed:

- [ ] 2004: `A special Daily Source Code moment.mp3`, `CultureShowPodcasting-2004-11-25.mp4`, `DaveAndAdamPhoneTest-2004-12-08.mp3`, `Podcasting.mp3` (Bloggercon III)
- [ ] 2005: `DSC-PPP-2005-03-06.mp3` (The First PP Podcast), `DSCV-01-2005-10-23.m4v`, `dsc.mp4`
- [ ] 2006: `DSC-2006-04-22-MysteryMashup.mp3`, `DSC-2006-06-16-1.mp3`, `DSC-2006-06-22-Katrina-Video-1.mov`, `DSC-2006-07-03-For-Mom.mp3`, `DSC-2006-10-31-1.mp3`, `DSC365--bestofMB01.mp3`, `DSC366--bestofMB02.mp3`, `DSC367--bestofMB03.mp3`, `dsc369_boc_anjibee.mp3`, `London Live Promo.m4v`
- [ ] 2007: `DSC-2007-01-01-BOC1.mp3` .. `DSC-2007-01-05-BOC5.mp3`, `DSC-2007-02-14-My-first-Show-directly-through-the-interface.mp3`, `DSC-2007-05-30-AC-VidBlaster-Test-1.mp4`, `-Test-2.mp4`, `DSC-2007-05-30-Darmstadt-Antanovs.mp4`, `DSC-2007-08-06-DNDS.mp3`
- [ ] 2008: `DSC-2008-04-05-XXX-Special-Announcement-From-Adam-Curry.mp3`, `DSC-2008-05-07-1.mp3`
- [ ] 2009: `821 It's Getting Hot In Here.mp3` (`821` is an old format stub)
- [ ] 2010: `DSC-2010-07-07-Special-Report-with-Bobbi-Eden.mp3`

Other shows found in the archive and feed: DevCast 1-6 (2006), PPP-2005-03-13, PSS-2005-05-19-2, Podshow20, QYDJ-ThingsAreBad, RVZR-2005-05-17, RVZR-2005-06-08, maryandkarla_HALLOWEEN_PROMO, Perversion For Profit #1 and PFP-002..004, TWiT-85-The-Podfather-2007-01-21, Curry on Stern-2010-06-14.



## Release: render for Adam (hosting, DNS)

Goal: render the feed with real-world values, hand it to Adam with what the
hosting needs, so he can put the show back online (e.g. dsc.curry.com). Not
rendered yet (sifting first). Open before rendering:

- [ ] 2026-10-26: Adam has been messaged about the progress and the hosting; waiting for his answer.
- [ ] Host: `feed: base_url` in `yaml/daily-source-code.yaml` (tentatively `https://dsc.curry.com`).
- [ ] Audio: 863 of 867 episodes have audio (archive, or a recovered copy in `mp3/` for `032` `051` `052` `208` `251`); the 4 others are skipped numbers. The enclosures still point at the dead original hosts (`m.podshow.com`, `mp3.dailysourcecode.podshow.com`, `m-uk.podshow.com`, `homepage.mac.com`, ...). Make release copies with all embedded images stripped (never touching the archive), served as `__BASE_URL__/mp3/...`, with `length` from the copies. The archive is 899 mp3s, 32 GB.
- [ ] Transcripts: 869 `srt/`, 16 `vtt/`; per-episode `podcast:transcript` url is a placeholder (`#daily-source-code-episode-pc20-transcript-NNN`, 822 episodes) to become `__BASE_URL__/srt/...` (`application/x-subrip`).
- [ ] Chapters: `chapters/` is empty; the 823 placeholders (`#daily-source-code-episode-pc20-chapters-NNN`) must be filled or the tag left out.
- [ ] Episode `itunes:image`: 824 placeholders (`#daily-source-code-episde-itunes-image-href-NNN`); leave out (channel art applies) unless an episode has its own art.
- [ ] Channel values to settle with Adam: `itunes:block` is True (hides the show from Apple), `podcast:block` per platform, `itunes:new-feed-url`, `podcast:locked` owner, `podcast:license` (empty; copyright says CC BY-NC-SA 3.0 US), `rawvoice:location` (Austin, Texas).
- [ ] `podcast:guid` `dfbbeceb-...` is not the UUIDv5 of `dailysourcecode.com/rss` (nor of `dsc.curry.com/rss`); fix it once the feed URL is final, and never change it after publishing.
- [ ] For Adam: storage about 32 GB plus transcripts and images; HTTPS; byte-range requests for the mp3s; correct MIME types (`audio/mpeg`, `application/x-subrip`, `image/png`); a DNS name (CNAME) for the host.

## Channel art (`img/channel/`)

- [ ] For the renovated feed the channel image must be 1400-3000 px square; the show's own images were 170-300 px. Overview, credits and status in [`img/channel/README.md`](../../img/channel/README.md).
  - [x] Choice: a stylised logo, not a photo. The first logo (`img/channel/dsc-logo.svg`, 3000 px PNG) is the channel image (decided 2026-10-26, a callback to the first episodes), Marchel's logo the alternative.
  - [x] Rendered for all feed uses: 3000/1400/144 px square, circle-safe, 16:9 and 9:16 (table in the README): SVG sources in `img/channel/`, iTunes renders in `img/itunes/`, podcast namespace renders in `img/podcast/`; `art-logo-2004.py` takes ASPECT and SCALE.
  - [ ] Hosting not decided: dailysourcecode.com is not ours (hoping for dsc.curry.com or similar, ask Adam). All feed URLs in `yaml/daily-source-code.yaml` use `__BASE_URL__`, filled from `feed: base_url` (tentatively `https://dsc.curry.com`) by `build.py`.
  - [ ] At render time: `<itunes:image>`, RSS `<image>` and `<podcast:image>` per purpose on the channel, episode art per item; re-released mp3s with all embedded images stripped (copies only, never the archive).
  - [x] The first logo (navy bands; an animated GIF on the blog's image host 2004-09-09, in the tags 2004-11 .. 12) and Marchel's logo (2004-12 .. 2005-10, purple 3D) reconstructed as SVG (`python/art-logo-2004.py`, `python/art-logo-2004-12.py`), with 3000 px PNG renders.
  - [ ] The Podfather picture (2005-06 .. 2008-03, by Craig Maloney per the show of 2005-06-17) is a photo montage of a Radio Veronica banner ("Dominee Curry live from Las Vegas", May 2004, 673x278), which Adam linked in the blog post "photoshop opportunity" (2005-06-17). The tag image is already at the banner's resolution; a large version needs Veronica's 2004 press photo (ask Adam; Veronica/SBS 2004 promo, photographer not credited anywhere found: file metadata, Dutch blog 2004-04-20 .. 06-02, web search). A black and white print ad of the same shoot ("Dominee Curry & the Crew", other pose) is on SoundCloud as cover art at 2172x2172, AI-upscaled; saved in `img/channel/found/`. Alternative photo: Adam with a microphone on an iPod (440x440 via geeksandbeats.com, 2014), source unknown.
  - [ ] The PodShow / Mevio show image (2006-07 .. 2013, painted portrait, "Daily Source Code with Adam Curry"): 300x300 at most (`psstatic.podshow.com/.../shows/med/deltasierracharl.png`, saved in `img/channel/found/`). Artist unknown; the lettering could be redrawn, the portrait needs a larger original.
  - [ ] Episode art 2010-2013 by the No Agenda art community (Randy Asher, Raymond Hagedoorn, Silicon Spin, CitizenX): larger originals may exist there; not searched yet.

## Episode yaml

- [x] `196.yaml` was invalid yaml (line 6, the apostrophe in "Breathe Don't Stop" ended the single-quoted description); the quote is now doubled.
- [x] 27 old format stubs without `podcast`/`fileinfo` (old numbers `059` `063` `143` `144` `156` `163` `190`-`195` `197`-`199` `225` `363` `488` `558` `621` `687` `688` `749` `755` `821` `856` `859`): resolved by the renumbering of 2026-10-26, except `687` `688` `856` `859` (skipped numbers).
- [ ] `111` and the other fixed episodes had a subtitle copied from the wrong file, replaced from the right file's tags.
- [ ] Episode numbers `008`, `009`, `018`, `028` .. are unquoted in some files; rewritten files quote them.
- [ ] **144 episodes `001`-`170` filled from the original posts** by `python/update-episodes-from-posts.py`, from `json/dsc-posts-2004-2005.json`. That file holds all 186 Daily Source Code category posts up to the #180 post: 138 from saved feeds in `rss/`, 48 from Wayback day pages and category captures. `source` gives the feed file or the Wayback capture URL. Only placeholders were replaced:
  - `link` and `guid.link`: the post permalink
  - `pubDate` (also in itunes/podcast): the post time. Feed items give it as GMT, Wayback posts as `dc:date`.
  - `enclosure` and `alternateEnclosure` url: the published mp3 URL
  - `description` and summaries: the post body, run through the same `parseDescription`/`cleanupHTML` as `update-episodes-from-rss.py`
  
  Titles were not changed. Enclosure lengths stay the archive size where the post came from a Wayback page (no length published there).
- [ ] Not filled from posts, to check:
  - `010` (title "Sunday August 22", show 2004-08-23)
  - `012` (title "Wednesday August 24", show 2004-08-25). The fragment titles say August 23 and 25, so the generated titles are one day off.
  - `129` (title 2005-03-02, mp3 2005-03-25)
  - the duplicates `014`/`015`, `018`/`019`, `130`/`146`
- [ ] **75 more episodes filled from posts after #180** (2005-05 .. 2006-06, 2007-03): `json/dsc-posts-2005-2007.json`, 80 posts from Wayback day pages of the category and of the main weblog. The 2007 template carries no `dc:date` (local time without zone), so `563` and `564` got link, guid and enclosure but no pubDate. Not filled:
  - `352`: its title and post #7270 say Tuesday March 14th 2006, but the mp3 and enclosure are `03-13-2006`
  - `395`: its title and post #7326 say Tuesday May 30th 2006, but the enclosure is `deltasierracharl-5745-05-29-2006.mp3`
  
  Recorded or published a day apart, to check.
- [x] No posts on Wayback for 2005-09-24 .. 2005-10-02, 2005-11-07 .. 09 and 2006-03-22 .. 24: filled from the live mirror, see below.
- [ ] **222 more episodes filled from the live mirror `http://radio-weblogs.com/0001014/`** (a static copy of radio.weblogs.com, last updated 2009-02-16): `json/dsc-posts-mirror.json`, 302 category posts not in the other post files, `source` is the mirror URL. The 504 day pages with posts were not kept: every post on them is in the post files.
  - 2005-06 .. 2006-06 with `dc:date` (pubDate), 2007-10 and 2008-03 .. 2009-02 (#665 .. #821) without (that template has no RDF, no pubDate written).
  - 320 day pages (2004-09-07, and 2006 .. 2008-02 except 2007-10) exist but say `[Macro error: The file "2006" wasn't found.]`: the posts were gone when Radio re-rendered them in 2008. Radio only writes day pages for days with a post, so these dates are DSC post days without content. They are listed in `json/dsc-mirror-macro-error-days.json`.
  - A show posted twice or with an extra on the same day: the post titled "Daily Source Code for …" is used (`239` #7133 not the RePod #7134, `255` #7159 not JobCast #7162, `310` #7222 not DSC-310-v2 #7224, `739` #354 not the Special Announcement #355).
  - Not filled, dates disagree: `222` (title 2005-08-13, file 2005-08-22, post #7116 has `DSC-222-2005-08-13.mp3`: `222` points at the 08-22 show, which is #225, and the archive `DSC-2005-08-13.mp3` is unused), `357` (post #7276 "Tuesday March 20th", enclosure 03-21), `374`/`375` (posts "April 25th"/"26th", enclosures 04-26/04-27), `668` (post #286 "October 8th 2007", enclosure 10-09), `793` (post #410 "September 23d 2008", enclosure 09-26: title copied from #792?).
  - Stated numbers that differ from the yaml number: `750` post titled #749, `756` titled #755.
- [ ] **440 episodes filled from the feed item extracts `rss/episodes/NNN.yaml`** by `python/update-episodes-from-extracts.py`. The extracts come from `update-episodes-from-rss.py`, whose `EPISODE_DIR` typo (`../yaml/epsodes/`) meant it never wrote episode yaml. They are numbered by feed order and drift from the show numbers (extract `019` is show `020` …), so they are matched by date. Only placeholders were replaced: `link`, `guid` (317 + 3 episodes), the `pubDate` timestamp in all three places (406), and the `enclosure`/`alternateEnclosure` url. Enclosure lengths stay the archive size, and descriptions were not touched.
  - From 2006 on the enclosure url carries the upload day, often a day off the show. 30 items matched no archive date and were matched by the date in their title, which agrees with the episode title in all 30 cases: `450` `474` `529` `574` `579` `581` `618` `669` `682` `683` `692` `693` `699` `714` `794` `797` `800` `843` `847` `850` `851` `852` `853` `855` `857` `858` `861` `863` `864` `865`.
  - `862`: the item `dailysourcecode-280880-05-15-2011.mp3` is titled "Daily Source Code for Tuesday April 16 3011", a typo for 2011 (`TITLE_FIXES` in the script). It was matched by that date. It was published on 2011-05-15 13:38:50 GMT, a month after the show and on the same day as `863` (`280882`). Its published link keeps the typo (`…/dsc-862-3011-04-16`) and was left as published. The item title is not used by the script; the episode title is unchanged.
  - **Corrected by the archive tags.** From 2006 on, the archive files carry the original post in their tags (TDES/comment), including "Direct link to the show", and often the item guid (TGID). `python/archive-tag-enclosures.py` lists these in `json/dsc-archive-tag-enclosures.json` (480 files; only `ffprobe` reads the archive). The first date-only pass had put a neighbouring show's item on several episodes, one show off, because Adam often uploaded the evening before. These are now matched by the tags: `561` `562` `583`-`590` `668` `695` `696`, and `408` `565` `582` `617` `680` `681` (the 2006-06-21 and 2007-03-20/04-17/04-26/11-01 double dates). The tag counts only when the file's title number (or else the item's stated "#NNN" or title date) agrees.
  - `670` was matched by the item's stated "#670" (its tags name it only by id). `815` and `818` were matched by tags only: the items are titled January 8 and January 19 2009, the episodes January 9 and January 20.
  - `489`: `DSC-2006-10-31.mp3` is tagged "#489 Daily Source Code for Tuesday October 31st 2006", but its embedded post and size (1354 bytes off the published length) are the 2006-11-02 item `34546`, so `489` now has that item. The 2006-10-31 item `34146` is `DSC-2006-10-31-1.mp3` (tagged #488, 1674 bytes off), which no episode uses. `488` is an old format stub.
  - Not corrected: `629` (`DSC-2007-07-05.mp3` is titled #629, but its tags hold #628's post, copied over; it keeps item `69430`, titled July 5), `750`/`756` (see below), and `121` `129` `132` `135` (2005 tags that link other shows).
  - **Feed items for shows that are in the archive but have no episode yaml.** These were compared by size; the 2004/2005 files were published unchanged:

    | Item | Archive file | Evidence | Episode |
    |---|---|---|---|
    | `DSC-2004-11-02.mp3` | `2004/DSC-2004-11-02.mp3` | same size | none |
    | `DSC-2004-11-10.mp3` | `2004/DSC-2004-11-10.mp3` | same size | none |
    | `DSC20041117.mp3` | `2004/DSC-2004-11-17.mp3` | same size, same audio as the adam.opml.org copy | none |
    | `DSC-2005-03-02.mp3` | `2005/DSC-2005-03-02.mp3` | same size | none (`129` is titled 03-02 but holds 03-25) |
    | `DSC-2005-03-03.mp3` | `2005/DSC-2005-03-03.mp3` | same size | none |
    | `DSC-2005-05-06.mp3` | `2005/DSC-2005-05-06.mp3` | 193 bytes off | none |
    | `DSC-222-2005-08-13.mp3` | `2005/DSC-2005-08-13.mp3` | 46645 bytes off (re-tagged as #222) | `222` holds 08-22 |
    | `dailysourcecode-34146` (2006-10-31) | `2006/DSC-2006-10-31-1.mp3` | tags #488 and the post, 1674 bytes | `488` stub |
    | `dailysourcecode-52931` (titled March 8 2007) | `2007/DSC-2007-03-07.mp3` | tags #558 and the post, 1864 bytes | `558` stub |
    | `dailysourcecode-109679` (2008-04-23) | `2008/DSC-2008-04-25.mp3` | tags #750 and the post | `750` holds `DSC-2008-04-18.mp3`, tagged #749 (item `108360`); `749` is a stub |
    | `dailysourcecode-111715` (2008-05-09) | `2008/DSC-2008-05-07-1.mp3` | tags #756 and the post | `756` holds `DSC-2008-05-07.mp3`, tagged #755 (item `111444`); `755` is a stub |
    | `dailysourcecode-137717` (2008-12-28) | `2008/DSC-2008-12-28.mp3` | tags "#813 … Sunday December 28th 2008", 7607 bytes | `813` holds `DSC-2008-12-31.mp3`, also tagged #813 ("DSC Year End Special 12-31-2008"): Adam numbered both #813 |
    | `dailysourcecode-143729` (2009-02-16) | `2009/821 It's Getting Hot In Here.mp3` | track 821, TGID is the item URL, 10574 bytes | `821` stub |

    Also `2007/DSC-2007-06-19.mp4` is tagged "#621 Daily Source Code VIDEO for Tuesday June 19th 2007" (`621` is a stub). The duplicates `014`/`015` (2004-08-27), `018`/`019` (2004-09-03) and `130`/`146` (2005-03-31) match their items by exact size. Making episodes for these waits on the renumbering decision.
  - Still unmatched: `DSC-2005-03-29.mp3`, the broken enclosure of `145`.
  - Descriptions: 23 episodes still had a placeholder description although their feed item has show notes: `216`-`218`, `222` (the notes of the 08-22 file it holds), `836` `837` `839` `841`-`848` `850`-`853` `855` `857` `858` `860`. They now have the item's description and summaries, filled the same way as from posts. Still without a description: the 2010 shows whose items were not saved (`838` `849` `854`), `867`, the stubs, and the duplicates `015` `019` `130` `146`.
  - [x] Episodes without any saved feed item, filled from the tags of their archive file (`python/update-episodes-from-tags.py`): the enclosure url ("Direct link to the show" / TGID) of `448` `451` `568` `838` `849` `854` `867`; link and guid of `448` `451` `568` from TGID (radio.weblogs.com permalinks `…/2006/08/24.html#a58`, `…/2006/08/29.html#a61`, `…/2007/03/23.html#a185`, in sequence with the neighbours); pubDate of `838` from the tag release time (2010-07-03T23:32:51Z). Their descriptions and subtitles were already taken from the tags.
  - [ ] Still no link/guid for `838` `849` `854` `867`: their TGID is the mp3 url, while the Mevio feed used `http://www.mevio.com/episode/<id>/dsc-NNN-YYYY-MM-DD` as guid. The ids are known (238567, 253455, 259791, 335227) but the page slug is not, so it is not filled in. `867`'s enclosure is dated 11-30-2013 while the file and title say 2013-11-27, and its tag track number is 687.
  - [ ] `015` `019` `130` `146` (the duplicates) still have no link/guid/enclosure url; they wait on the renumbering decision.
  - `813`: the extract `rss/episodes/813.5.yaml` (item `138006`, 2008-12-31) had been skipped by the file glob. It now fills `813`, whose file is tagged "#813 DSC Year End Special 12-31-2008".
- [x] `podcast.alternateEnclosure` is a list, one entry per source. 817 episodes had the stub generator's single mapping with a list of uris; rewritten as the list (bitrate `None000` emptied). `update-episodes-from-audio.py` now does the same when it meets the old shape.
- [x] Stub generator bug: on days where month and day are equal (07-07, 08-08, 12-12 …) `alternateEnclosure` held the month-end show's file and length (`204` had `DSC-2005-07-29.mp3`, 21178506 bytes, #217's). Fixed in 24 episodes (`023` `058` `111` `162` `179` `204` `221` `238` `257` `277` `296` `346` `381` `400` `437` `538` `576` `630` `699` `730` `743` `766` `781` `788`), now the episode's own enclosure with the measured length.
- [ ] `145` (2005-03-30): the post's own enclosure was broken. `enclosure.url` now points at `DSC-2005-03-30.mp3`, the file linked from the same post on the day page. The summary keeps the published body, which still links `DSC-2005-03-29.mp3`.



## Show notes (`shownotes/`)

- [x] Show notes are kept as OPML only. The HTML renderings found on Wayback were distilled to OPML with `python/opml-from-html.py`, then removed (they remain in git history and on Wayback).
- [x] Original OPML found on Wayback:
  - 2004-11-01, 11-02, 11-03, 11-29 and 12-16 from blognewsnetwork.com/members/0000001/opml/ (the earliest capture; later captures are parked-domain pages).
  - 2004-11-22, 11-23, 11-24, 11-30, 12-01 and 12-03 from live.curry.com/opml/.
  - 2005-08-31 .. 09-12 from mp3.dailysourcecode.podshow.com (OmniOutliner).
- [x] `opml-from-html.py` was checked on the 17 dates that had both a rendering and the original OPML. All 3,113 nodes come back identical (text, depth, links, empty nodes, MacRoman bytes) except on 2004-11-22: there the OPML was edited after the rendering was captured (rendering 11-25, OPML 12-04), and 3 nodes differ (`\'` escapes and `&lt;outlines&gt;` from a comment form). The earlier state is kept as `2004/DSC-2004-11-22-20041125.opml`. Lost in a rendering: Radio's song attributes (artist, album, `f`, `sizeFile`, `whenFileCreated`) and `#title`.
- [x] Rebuilt from a rendering, because no original OPML was found: 2004-11-05, 11-09, 11-10, 11-11, 11-15, 2005-08-29 and 08-30. Each starts with a `<!-- Reconstructed from the … HTML … -->` comment. NUL characters are left out.
- [ ] 2004-11-11: the renderer wrote `Casta"eda` (Castañeda), the original byte is lost.
- [x] NUL characters removed from the 11 Radio OPML originals that had them (2004-11-01, 11-02, 11-03, 11-16, 11-17, 11-22, 11-23, 11-29, 11-30, 12-01, 12-16; 3 to 48 each, at the ends of texts). XML cannot hold NUL, and the files are now valid. All of `shownotes/` is valid XML.
- [x] The ipodder directory OPMLs (`opml/ipodder*`) are kept elsewhere as podcast OPMLs and are out of scope here. They were not fixed: `ipodderDirectory-2004-10-11.opml` and `-2004-12-30.opml` use `&auml;`.



## Transcripts (`srt/`)

- [x] Checked all 868 srt files against the audio length. Re-transcribed with faster-whisper "small" (`python/srt-transcribe.py`), with the music step applied:
  - `2005/DSC-2005-10-02.srt` covered only 31%: it was made from the zero-filled archive copy. Now made from the recovered `mp3/2005/DSC-2005-10-02.mp3` (01:04:00).
  - `2005/DSC-2005-07-14.srt` did not exist; made from `mp3/2005/DSC-2005-07-14.mp3`.
  - `2004/DSC-2004-09-27.srt` covered 85% and its time codes went backwards; now the whole show.
- [ ] Song lyrics: `python/srt-music.py` finds songs with the PANNs audio tagger (Music > 0.5 and Speech < 0.1 on 5 s windows, runs of 20 s or more) and replaces the lyric cues with one `[ Music ]` cue spanning the song. Talking over a music bed is kept, and so are the cues in the first and last 6 s of a song (Adam talks over song intros: "coming to you from Northern California. San Francisco. Curry Condo" in 2006-03-24 was lost before this margin). A batch over all transcripts is running (rewrites `srt/*/*.srt` in place, scores cached in `~/.cache/dsc-music/`).
  - Status 2026-10-26: up to 2006-09-20; 350 transcripts with songs replaced, 111 where the tagger crashed ("Illegal instruction", intermittent), 2005-10-02 skipped (already done from the recovered mp3). A retry pass runs the crashed ones again (3 tries each) when the batch is done.
  - The 351 transcripts done before the 6 s margin were redone from their committed version (checked first: the committed version with the old step gave exactly the file on disk); 681 cues came back. `2005/DSC-2005-07-14.srt` is not committed and keeps the old result.
- [ ] 38 srt files have no matching episode (shows missing from the yaml).

## Locations (`yaml/locations.yaml`)

Recording locations only: where each show was recorded, not the places Adam talks about. Pipeline (scripts in `python/`):
`locations-extract.py` (spaCy over transcripts, show notes, descriptions) → `locations-geocode.py` (GeoNames dump, offline; the names are only used to recognise places) → `locations-timeline.py` (per show: a hand-set `recorded` period, else the show notes "From …", else the transcript intro "coming to you from …" / "I'm at the …"; "here in the UK" only confirms or breaks a carried location; for a show with no place or only a country, Adam's blog post of the same day or the day before, from `json/blog-posts.json` collected by `blog-posts.py` from the saved feeds and Wayback day pages: "I'm in …", "live from …", "back in …") → `locations-build.py` (Nominatim for venues, Wikidata for OSM ids, OpenTopoData SRTM for altitude; curated entries are kept, generated ones rebuilt). The episode yaml is not touched.

- [x] After the renumbering (2026-10-26, rerun of extract, geocode, timeline and build): 860 show dates: 356 located by the show notes, 213 by the transcript, 6 by the blog, 5 by a country or region only, 1 by hand; 244 carried, 35 confirmed; 168 periods, 60 locations (38 curated, 52 with coordinates, 8 to resolve). New: Cannes (2007-06-19, #621 "From Cannes, French Riviera", the notes now taken raw from the feed item), #750 San Francisco on its real date 2008-04-23 (blog), #756 Curry Manor 2008-05-09 (confirmed); the new episodes without a stated place are carried. 2005-03-29 is gone (the broken upload, not a show). Paris Hill, Street and Tulsa fell below the two-mention threshold (the duplicate yaml are gone); none was a recording location.
- [x] `locations-timeline.py`: the show date is the date in the audio file name, else the title, else the pubDate (`821`, `051`, `052` have none in the name); `SHOW_DATE_FIXES` maps the misnamed `2008/DSC-2008-04-25.mp3` (#750, 2008-04-23) and `2008/DSC-2008-05-07-1.mp3` (#756, 2008-05-09), transcripts included. `locations-build.py` now waits `PACE` = 12 s between web requests (was 1.5-2 s).
- [x] Before the renumbering: 854 show dates: 352 located by the show notes, 215 by the transcript, 6 by the blog, 5 by a country or region only (1 of them from the blog), 1 by hand; 240 carried from the show before; 35 confirmed (a country/continent statement that fits, a region within 400 km, or a town within 25 km of the residence or venue carried, e.g. "here in Guildford" at the Curry Manor). Every show date has a location. `locations.yaml`: 59 locations, 51 with WGS-84 coordinates.
- [x] Transcript patterns besides "coming to you from": "the town of Utrecht", "in Berkeley, California" (a town with its state or country), "on British Airways flight 442" (the "In flight" vehicle: 2004-11-09 and 2005-02-26, both San Francisco to London). Whisper's "Starbox ... Guildford" is the Starbucks on Market Street (2004-12-03), "the career manager" is the Curry Manor (2008-04-29). "Coming to you from San Francisco, last time we spoke ... I was in Curry Cottage" (2005-07-22): the phrase is cut at back-references ("last time", "when I was", "yesterday").
- [x] 2006 show notes start with the template line "From Curry Cottage, Guildford, UK" even when the show was elsewhere; a later "live from ..." in the notes wins: 2006-10-03 "we are live from Roundhouse in London!" (Digital Music Awards; Roundhouse added as a venue). Not 2006-10-02, where only the blog says "Live From London. We're still building our set" (the notes win over the blog), nor 10-04 ("the day after our Live From London extravaganza").
- [ ] Blog posts (`json/blog-posts.json`, 2241 posts): from the saved feeds, plus Wayback day pages for the shows without a stated place and the day before (radio.weblogs.com 2001-11 .. 2008, www.curry.com 2004-12 .. 2006-02, curry.podshow.com `?p=N` posts dated by interpolation from 46 known ids). Status 2026-10-26: all 506 pages fetched (paced, 10-15 s apart; 2649 posts): radio.weblogs and curry.com day pages (Manila day pages mark posts like Radio), 251 podshow posts (WordPress: date from "Posted on", comments left out). Some 2008 radio.weblogs captures are labelled gzip but are plain HTML; several 2008 day pages are truncated captures (3 KB, no post text). A post counts for the show of its day or the day after; for a show that would otherwise be carried, up to 2 days after. Used: "First day back in Belgium" (2004-08-13), "I'm in SF, arrived safely yesterday afternoon" (2006-02-20, podshow ?p=8), "I'm in San Francisco again for a few days" (2008-01-24, ?p=942), "Live from the Curry Condo" (2008-02-22), "I'm back in San Francisco, and have a show to be done this evening" (2008-04-23, ?p=1067; the show is 04-25). Rejected: "Live from the infield at the Kentucky Derby" (a clip in the show), "the power comes back in South Park" (the office), "Father Vonhögen is a priest from the Netherlands" (a guest).
- [ ] 2004-08-13 .. 08-15 (the first shows) state no location; the blog of 2004-08-13 says "First day back in Belgium" (radio.weblogs.com/0001014/2004/08/13.html#a6310), so Belgium (country only; Curry Castle from 08-16).
- [ ] The old hand-set periods were replaced by the computed `at` periods: Curry Castle 2004-08-13 .. 2004-11-18, Curry Cottage 2004-11-19 .. 2008-11-31 (not a date), Curry Manor .. 2008-12-01. The show notes say "From The Curry Manor" from #535 (2007-01). Only Bell Harbor's 2005-06-25 is kept, as `recorded` (hand-set periods that win over the transcripts).
- [ ] Curry Manor was placed in South London (51.3895, -0.0766); the show notes say Guildford 176 times ("on the West Side of G-Town"). Now Guildford, town precision.
- [ ] Curry Castle: the coordinates in `locations.yaml` (51.330813, 4.766188) differ from the `podcast.location.geo` of the episodes (51.3480, 4.7176).
- [ ] For Adam, or research (not resolved or town precision only; residence addresses are deliberately not looked up):
  - Curry Manor (Guildford), Curry Terrace ("an end of terrace house ... on a square" in southwest London, from 2008-12), Curry Condo (San Francisco, "overlooking the Bay Bridge"), Curry Bunker (Keizersgracht, Amsterdam, a former museum), Hilltop Watchtower / Crackpot Command Center (Southern California, Los Angeles area, 2010), Camp Mofo (Austin, 2012).
  - W Hotel New York (#561-#563, which W?), PodShow HQ (San Francisco / Los Angeles offices; the San Francisco office was in South Park, SoMa, per the blog of 2006-02-20), the KPCB CEO Summit venue in Monterey (#394), "Ricky's" (srt/2004/DSC-2004-11-05.srt, garbled; possibly Rickey's Hyatt in Palo Alto: the blog of 2004-11-08 has "Live from Palo Alto, it's Trade Secrets!" for Trade Secrets of 11-07 with Dave Winer, and 11-09 was recorded on the flight from San Francisco to London).
  - Hotels that have since been renamed: Tribeca Grand (now The Roxy Hotel), Pan Pacific San Francisco (500 Post Street), Clift (Clift Royal Sonesta); looked up by today's name or address.
  - Vehicles have no fixed place: Studio A8 (Audi A8), N277DS (aircraft, tail number), The Magnum (rented Dodge Magnum), In flight (airline flights).
- [ ] Country or region precision only, to pin to a specific place later (add a `recorded` period to a precise location; it wins over the country statement):
  - Belgium 2004-08-13 .. 08-15 (blog "back in Belgium"; Curry Castle from 08-16?)
  - Netherlands 2004-09-06 .. 09-09 ("here in the Netherlands. And I was an invited guest, which meant I got to fly in"; 09-09 "here in the press in the Netherlands"). Doubtful: the 09-06 statement is about the air show of Saturday 09-04 ("Laylee's South", Lelystad?), not where Monday's show was recorded; the blog of 09-01 says "Today I finalize the Amsterdam Heliport deal, so I have to travel most of the day". Curry Castle (Belgium) is as likely.
  - Belgium 2004-09-11 .. 09-19 ("coming to you from a rather balmy Belgium", 09-15 "I'm in Belgium"; Curry Castle?)
  - Northern California 2006-03-15 ("Coming to you from northern California"; Curry Condo, San Francisco, from 03-16)
  - United Kingdom 2008-11-18 ("here in the United Kingdom"; between Curry Manor and Curry Terrace)
- [ ] Carried periods are an assumption: Adam travelled between Europe and the US a lot; `stated` and `confirmed` per period show how much is backed by the shows.

## Dates

- [ ] The episode date is primary, the publish date secondary (same day or any day later). Date only `pubDate` values in the episode yaml are placeholders for the episode date, not publish dates.
- [ ] mp3 `TDRL` tags hold a release timestamp in 458 files (kept in `json/audio-metadata.json`), a source for real publish dates.
- [ ] 53 transcripts where the date or weekday Adam says differs from the mp3 date, see "Spoken dates" in `dsc-timeline.md`. Many are one day off ("It's Monday" in a Tuesday file): recorded one day, named after the publish day? Some are mentions of other days.
- [ ] The month end fixes set `pubDate` to the episode date of the correct file, like the other stubs; the real publish date is unknown.



## Episode yaml formatting

- [ ] `001.yaml` lost the blank lines between list entries under `socialInteract` and `alternateEnclosure` when rewritten, data unchanged.
- [ ] Multi line show notes are written as `|` literal blocks, trailing whitespace on lines trimmed, tabs kept.



## Timeline (`dsc-timeline.md`)

- [ ] Duplicate rows were dropped when the table was regenerated (originals in git HEAD): `182` 2005-06-13, `255` 2005-10-06, `382`, `482`, `582` 2007-04-17.
- [ ] 242 episodes with dates disagreeing between sources, see "Date conflicts" in `dsc-timeline.md`.
