# Episodes - Irregularities

Found while cross checking episode yaml, RSS fragments (`rss/`), transcripts (`srt/`), the timeline (`dsc-timeline.md`) and the audio archive (`/media/chrise/work/audio/dsc/DSC`, read only). To be checked later.

Status: `[ ]` open, `[x]` resolved.



## Numbering

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
- [ ] `2005/DSC-2005-07-14.mp3.txt` starts with an ID3 tag (`#208 DSC-2005-07-14`) but ffprobe can't read it, probably truncated. `208` has no usable audio.
- [ ] `255` points at `DSC-255-2005-10-06-JobCast.mp3`, the archive has both `DSC-2005-10-06-JobCast.mp3` and `DSC-2005-10-06.mp3`. Not matched, which one is episode 255?
- [ ] `582` matched to `2007/DSC-2007-04-17-repost.mp3`, confirm it is the 2007-04-17 show.
- [ ] `818` matched to `2009/818 DSC-818-2009-01-2009.mp3` (date in name broken, tags say #818).
- [ ] `206` (`DSC-206B-2005-07-11.mp3`) and `770` (`DSC-770-2008-06-18.mp3`) matched to `DSC-2005-07-11.mp3` and `DSC-2008-06-18.mp3`.
- [ ] `Misc/` holds copies of 2005-01-07, 2005-01-10, 2005-01-19 and numbered copies of 259-262, 336 and 867; `Misc/DSC-2005-01-19.mp3` has the title `2DSC-005-01-19`.
- [x] Durations in the episode yaml were a few seconds off; now replaced by a full decode (e.g. `001` 1357 → 1350, `020` 2469 → 2466).
- [ ] Probably truncated or damaged, they decode much shorter than their header says: `2005/DSC-2005-10-02.mp3` (44 min short), `2009/DSC-2009-01-09.mp3` (5.6 min), `2009/DSC-2009-01-07.mp3` (1.5 min). The decoded (playable) length is used.
- [ ] `018` had size 32195843 (another copy of the file?), now the size of the archive `DSC-2004-09-03.mp3`, 27984382, the same file as `019`.

### Archive files not used by any episode

Regular show dates, most likely missing or misnumbered episodes:

- [ ] 2004-08-26, 2004-09-02, 2004-11-02, 2004-11-04, 2004-11-09, 2004-11-10, 2004-11-17
- [ ] 2005-03-02, 2005-03-03, 2005-04-21, 2005-05-06, 2005-08-13, 2005-10-06
- [ ] 2006-03-29, 2006-05-06, 2006-03-20/21/22/25 (`.m4v`, video versions?)
- [ ] 2007-03-07, 2007-06-19 (`.mp4`)
- [ ] 2008-04-25, 2008-12-28

Specials and extra parts, decide whether they belong in the feed:

- [ ] 2004: `A special Daily Source Code moment.mp3`, `CultureShowPodcasting-2004-11-25.mp4`, `DaveAndAdamPhoneTest-2004-12-08.mp3`, `Podcasting.mp3` (Bloggercon III)
- [ ] 2005: `DSC-PPP-2005-03-06.mp3` (The First PP Podcast), `DSCV-01-2005-10-23.m4v`, `dsc.mp4`
- [ ] 2006: `DSC-2006-04-22-MysteryMashup.mp3`, `DSC-2006-06-16-1.mp3`, `DSC-2006-06-22-Katrina-Video-1.mov`, `DSC-2006-07-03-For-Mom.mp3`, `DSC-2006-10-31-1.mp3`, `DSC365--bestofMB01.mp3`, `DSC366--bestofMB02.mp3`, `DSC367--bestofMB03.mp3`, `dsc369_boc_anjibee.mp3`, `London Live Promo.m4v`
- [ ] 2007: `DSC-2007-01-01-BOC1.mp3` .. `DSC-2007-01-05-BOC5.mp3`, `DSC-2007-02-14-My-first-Show-directly-through-the-interface.mp3`, `DSC-2007-05-30-AC-VidBlaster-Test-1.mp4`, `-Test-2.mp4`, `DSC-2007-05-30-Darmstadt-Antanovs.mp4`, `DSC-2007-08-06-DNDS.mp3`
- [ ] 2008: `DSC-2008-04-05-XXX-Special-Announcement-From-Adam-Curry.mp3`, `DSC-2008-05-07-1.mp3`
- [ ] 2009: `821 It's Getting Hot In Here.mp3` (`821` is an old format stub)
- [ ] 2010: `DSC-2010-07-07-Special-Report-with-Bobbi-Eden.mp3`

Other shows found in the archive and feed: DevCast 1-6 (2006), PPP-2005-03-13, PSS-2005-05-19-2, Podshow20, QYDJ-ThingsAreBad, RVZR-2005-05-17, RVZR-2005-06-08, maryandkarla_HALLOWEEN_PROMO, Perversion For Profit #1 and PFP-002..004, TWiT-85-The-Podfather-2007-01-21, Curry on Stern-2010-06-14.



## Episode yaml

- [ ] `196.yaml` is invalid yaml (line 6, unquoted description), `build.py` will fail on it.
- [ ] 27 old format stubs without `podcast`/`fileinfo`: `059` `063` `143` `144` `156` `163` `190`-`195` `197`-`199` `225` `363` `488` `558` `621` `687` `688` `749` `755` `821` `856` `859`. Not decorated from audio.
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
- [ ] No posts on Wayback for 2005-09-24 .. 2005-10-02, 2005-11-07 .. 09 and 2006-03-22 .. 24: the captured day pages are empty shells. These stay RSS hunting periods, together with 2007-03-20 .. 23 and 2010-12 .. 2011-05.
- [ ] `145` (2005-03-30): the post's own enclosure was broken. `enclosure.url` now points at `DSC-2005-03-30.mp3`, the file linked from the same post on the day page. The summary keeps the published body, which still links `DSC-2005-03-29.mp3`.



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
