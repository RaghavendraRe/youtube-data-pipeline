// YouTube Data Collection - Power Query M Code
// Paste this into Power BI Desktop > Get Data > Blank Query > Advanced Editor

let
    // ========== CONFIGURATION ==========
    API_KEY = "AIzaSyBM5DU838aPORBzQE7L3Hv1q7PGSEQlGU",
    CHANNEL_ID = "UCUDKhNE_Y_DVkFx1nFNZTWQ",
    
    // Official podcast titles to filter
    OfficialPodcasts = {
        "Mindful Moments | Brahma Kumaris Podcast",
        "Climate Wisdom - COP30 Belem, Brasil",
        "The Spiritual Empress - Dadi Prakashmani",
        "COP 29 Baku - Climate Wisdom | Brahma Kumaris",
        "Care, Share, Inspire - Climate Wisdom from COP28 Dubai",
        "Companion of God - Dadi Janki (with English Translation)"
    },
    
    // ========== HELPER FUNCTIONS ==========
    
    // Build YouTube API URL
    GetApiUrl = (endpoint as text) as text =>
        "https://www.googleapis.com/youtube/v3/" & endpoint & "?key=" & API_KEY,
    
    // Parse ISO 8601 duration to seconds
    ParseDuration = (duration as text) as number =>
        let
            hours = try Number.FromText(Text.BetweenDelimiters(duration, "PT", "H")) otherwise 0,
            minutes = try Number.FromText(Text.BetweenDelimiters(duration, "H", "M")) otherwise 
                      try Number.FromText(Text.BetweenDelimiters(duration, "PT", "M")) otherwise 0,
            seconds = try Number.FromText(Text.BetweenDelimiters(duration, "M", "S")) otherwise 
                      try Number.FromText(Text.BetweenDelimiters(duration, "PT", "S")) otherwise 0
        in
            hours * 3600 + minutes * 60 + seconds,
    
    // ========== STEP 1: Get Uploads Playlist ID ==========
    ChannelUrl = GetApiUrl("channels") & "&id=" & CHANNEL_ID & "&part=contentDetails",
    ChannelJson = Json.Document(Web.Contents(ChannelUrl)),
    UploadsPlaylistId = ChannelJson[items]{0}[contentDetails][relatedPlaylists][uploads],
    
    // ========== STEP 2: Get All Playlists ==========
    GetAllPlaylists = () =>
        let
            GetPlaylistPage = (pageToken as nullable text) as record =>
                let
                    url = GetApiUrl("playlists") & "&channelId=" & CHANNEL_ID & "&part=snippet&maxResults=50" &
                          (if pageToken <> null then "&pageToken=" & pageToken else ""),
                    json = Json.Document(Web.Contents(url)),
                    items = try json[items] otherwise {},
                    nextToken = try json[nextPageToken] otherwise null
                in
                    [Items = items, NextToken = nextToken],
            
            GetAllPages = List.Generate(
                () => GetPlaylistPage(null),
                each [Items] <> null and List.Count([Items]) > 0,
                each GetPlaylistPage([NextToken]),
                each [Items]
            ),
            
            AllItems = List.Combine(GetAllPages),
            // Check if we have items before creating table
            Result = if List.Count(AllItems) = 0 then 
                #table({"PlaylistId", "PlaylistTitle"}, {})
            else
                let
                    ToTable = Table.FromList(AllItems, Splitter.SplitByNothing(), {"Column1"}, null, ExtraValues.Error),
                    Expanded = Table.ExpandRecordColumn(ToTable, "Column1", {"id", "snippet"}),
                    ExpandedSnippet = Table.ExpandRecordColumn(Expanded, "snippet", {"title"}),
                    Renamed = Table.RenameColumns(ExpandedSnippet, {{"id", "PlaylistId"}, {"title", "PlaylistTitle"}})
                in
                    Renamed
        in
            Result,
    
    AllPlaylists = GetAllPlaylists(),
    
    // ========== STEP 3: Map Videos to Playlists ==========
    GetVideosInPlaylist = (playlistId as text) =>
        let
            GetPage = (pageToken as nullable text) =>
                let
                    url = GetApiUrl("playlistItems") & "&playlistId=" & playlistId & "&part=contentDetails&maxResults=50" &
                          (if pageToken <> null then "&pageToken=" & pageToken else ""),
                    json = Json.Document(Web.Contents(url)),
                    items = try json[items] otherwise {},
                    nextToken = try json[nextPageToken] otherwise null
                in
                    [Items = items, NextToken = nextToken],
            
            AllPages = List.Generate(
                () => GetPage(null),
                each [Items] <> null and List.Count([Items]) > 0,
                each GetPage([NextToken]),
                each [Items]
            ),
            
            AllItems = List.Combine(AllPages),
            VideoIds = List.Transform(AllItems, each [contentDetails][videoId])
        in
            VideoIds,
    
    // Create video-to-playlist mapping
    PlaylistMapping = Table.AddColumn(AllPlaylists, "VideoIds", each GetVideosInPlaylist([PlaylistId])),
    ExpandedVideos = Table.ExpandListColumn(PlaylistMapping, "VideoIds"),
    VideoPlaylistMap = Table.Group(ExpandedVideos, {"VideoIds"}, {
        {"AllPlaylists", each Text.Combine([PlaylistTitle], "|"), type text},
        {"OfficialPodcast", each 
            let
                officialMatches = List.Select([PlaylistTitle], (pl) => 
                    List.AnyTrue(List.Transform(OfficialPodcasts, (official) => 
                        Text.Contains(pl, official) or Text.Contains(official, pl)
                    ))
                )
            in
                if List.Count(officialMatches) > 0 then Text.Combine(officialMatches, "|") else null,
            type nullable text}
    }),
    
    // ========== STEP 4: Get Videos from Uploads (Last 2 Years) ==========
    TwoYearsAgo = DateTime.AddDays(DateTime.LocalNow(), -730),
    
    GetUploadVideos = () =>
        let
            GetPage = (pageToken as nullable text) =>
                let
                    url = GetApiUrl("playlistItems") & "&playlistId=" & UploadsPlaylistId & "&part=snippet,contentDetails&maxResults=50" &
                          (if pageToken <> null then "&pageToken=" & pageToken else ""),
                    json = Json.Document(Web.Contents(url)),
                    items = try json[items] otherwise {},
                    nextToken = try json[nextPageToken] otherwise null
                in
                    [Items = items, NextToken = nextToken],
            
            AllPages = List.Generate(
                () => GetPage(null),
                each [Items] <> null and List.Count([Items]) > 0,
                each GetPage([NextToken]),
                each [Items]
            ),
            
            AllItems = List.Combine(AllPages),
            ToTable = Table.FromList(AllItems, Splitter.SplitByNothing(), {"Column1"}, null, ExtraValues.Error),
            Expanded = Table.ExpandRecordColumn(ToTable, "Column1", {"snippet", "contentDetails"}),
            ExpandedSnippet = Table.ExpandRecordColumn(Expanded, "snippet", {"publishedAt"}),
            ExpandedContent = Table.ExpandRecordColumn(ExpandedSnippet, "contentDetails", {"videoId"}),
            AddedPublishDate = Table.TransformColumns(ExpandedContent, {
                {"publishedAt", each DateTime.FromText(_, [Format="yyyy-MM-ddTHH:mm:ssZ"]), type datetime}
            }),
            FilteredByDate = Table.SelectRows(AddedPublishDate, each [publishedAt] >= TwoYearsAgo)
        in
            FilteredByDate,
    
    UploadVideos = GetUploadVideos(),
    VideoIdList = UploadVideos[videoId],
    
    // ========== STEP 5: Get Video Details in Batches ==========
    BatchSize = 50,
    
    GetVideoDetails = (videoIds as list) =>
        let
            url = GetApiUrl("videos") & "&id=" & Text.Combine(videoIds, ",") & "&part=snippet,contentDetails,statistics,liveStreamingDetails",
            json = Json.Document(Web.Contents(url)),
            items = try json[items] otherwise {}
        in
            items,
    
    // Create batches
    VideoIdBatches = List.Generate(
        () => [i = 0],
        each [i] < List.Count(VideoIdList),
        each [i = [i] + BatchSize],
        each List.FirstN(List.Skip(VideoIdList, [i]), BatchSize)
    ),
    
    // Fetch all video details
    AllVideoDetails = List.Transform(VideoIdBatches, each GetVideoDetails(_)),
    CombinedDetails = List.Combine(AllVideoDetails),
    
    // ========== STEP 6: Transform to Table with Calculated Metrics ==========
    DetailsTable = Table.FromList(CombinedDetails, Splitter.SplitByNothing(), {"Column1"}, null, ExtraValues.Error),
    ExpandedDetails = Table.ExpandRecordColumn(DetailsTable, "Column1", 
        {"id", "snippet", "contentDetails", "statistics", "liveStreamingDetails"}),
    
    // Expand all nested fields
    ExpandedSnippet2 = Table.ExpandRecordColumn(ExpandedDetails, "snippet", 
        {"title", "description", "publishedAt", "tags", "categoryId", "channelTitle"}),
    ExpandedContent2 = Table.ExpandRecordColumn(ExpandedSnippet2, "contentDetails", 
        {"duration", "definition"}),
    ExpandedStats = Table.ExpandRecordColumn(ExpandedContent2, "statistics", 
        {"viewCount", "likeCount", "commentCount"}),
    
    // Handle liveStreamingDetails (may be null)
    ExpandedLive = Table.ExpandRecordColumn(ExpandedStats, "liveStreamingDetails", 
        {"actualStartTime", "actualEndTime"}, {"actualStartTime", "actualEndTime"}),
    
    // Add calculated columns
    AddedDurationSec = Table.AddColumn(ExpandedLive, "Duration (Sec)", each 
        ParseDuration([duration]), type number),
    
    AddedIsShort = Table.AddColumn(AddedDurationSec, "Is Short", each 
        [#"Duration (Sec)"] > 0 and [#"Duration (Sec)"] <= 60, type logical),
    
    AddedIsLive = Table.AddColumn(AddedIsShort, "Is Live", each 
        [actualStartTime] <> null, type logical),
    
    AddedVideoType = Table.AddColumn(AddedIsLive, "Video Type", each 
        if [Is Live] then "Live" 
        else if [Is Short] then "Short" 
        else "Long", type text),
    
    // Convert stats to numbers
    ConvertedStats = Table.TransformColumnTypes(AddedVideoType, {
        {"viewCount", Int64.Type},
        {"likeCount", Int64.Type},
        {"commentCount", Int64.Type}
    }),
    
    // Replace nulls with 0 for calculations
    ReplacedNulls = Table.ReplaceValue(ConvertedStats, null, 0, Replacer.ReplaceValue, {"viewCount", "likeCount", "commentCount"}),
    
    // Add engagement metrics
    AddedEngagement = Table.AddColumn(ReplacedNulls, "Engagement", each 
        [likeCount] + [commentCount], type number),
    
    AddedEngagementRate = Table.AddColumn(AddedEngagement, "Engagement Rate", each 
        if [viewCount] > 0 then Number.Round(([likeCount] + [commentCount]) / [viewCount], 4) else 0, type number),
    
    // Add Tags as text
    AddedTags = Table.AddColumn(AddedEngagementRate, "Tags Text", each 
        if [tags] <> null then Text.Combine([tags], "|") else "", type text),
    
    // Format published date
    FormattedDate = Table.TransformColumns(AddedTags, {
        {"publishedAt", each DateTime.ToText(DateTime.FromText(_), "yyyy-MM-dd HH:mm:ss"), type text}
    }),
    
    // Add current timestamp
    CurrentTime = DateTime.ToText(DateTime.LocalNow(), "yyyy-MM-dd HH:mm:ss"),
    AddedTimestamps = Table.AddColumn(FormattedDate, "First Fetched At", each CurrentTime, type text),
    AddedTimestamps2 = Table.AddColumn(AddedTimestamps, "Last Fetched At", each CurrentTime, type text),
    
    // Add Video URL
    AddedUrl = Table.AddColumn(AddedTimestamps2, "Video URL", each 
        "https://www.youtube.com/watch?v=" & [id], type text),
    
    // ========== STEP 7: Merge with Playlist Mapping ==========
    MergedWithPlaylists = Table.NestedJoin(AddedUrl, {"id"}, VideoPlaylistMap, {"VideoIds"}, "PlaylistInfo", JoinKind.LeftOuter),
    ExpandedPlaylists = Table.ExpandTableColumn(MergedWithPlaylists, "PlaylistInfo", {"AllPlaylists", "OfficialPodcast"}),
    
    // ========== STEP 8: Final Column Renaming and Selection ==========
    FinalTable = Table.SelectColumns(ExpandedPlaylists, {
        "id", "Video URL", "title", "description", "publishedAt", "Duration (Sec)", "duration",
        "Is Short", "Is Live", "Video Type", "viewCount", "likeCount", "commentCount",
        "Engagement", "Engagement Rate", "Tags Text", "AllPlaylists", "OfficialPodcast",
        "categoryId", "channelTitle", "definition", "actualStartTime", "actualEndTime",
        "First Fetched At", "Last Fetched At"
    }),
    
    RenamedColumns = Table.RenameColumns(FinalTable, {
        {"id", "Video ID"},
        {"title", "Title"},
        {"description", "Description"},
        {"publishedAt", "Published Date"},
        {"duration", "Duration (ISO)"},
        {"viewCount", "Views"},
        {"likeCount", "Likes"},
        {"commentCount", "Comments"},
        {"Tags Text", "Tags"},
        {"AllPlaylists", "All Playlists"},
        {"OfficialPodcast", "Podcast Name"},
        {"categoryId", "Category ID"},
        {"channelTitle", "Channel Title"},
        {"definition", "Definition (HD/SD)"},
        {"actualStartTime", "Live Start"},
        {"actualEndTime", "Live End"}
    })
in
    RenamedColumns
