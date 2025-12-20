// YouTube Data Collection - SIMPLIFIED VERSION (Working)
// Paste this into Power BI Desktop > Get Data > Blank Query > Advanced Editor

let
    // ========== CONFIGURATION ==========
    API_KEY = "AIzaSyBM5DU838aPORBzQE7L3Hv1q7PGSEQlGU",
    CHANNEL_ID = "UCUDKhNE_Y_DVkFx1nFNZTWQ",
    
    // ========== HELPER FUNCTIONS ==========
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
    
    // ========== STEP 2: Get Videos from Uploads ==========
    GetUploadVideos = () =>
        let
            GetPage = (pageToken as nullable text, counter as number) =>
                let
                    url = GetApiUrl("playlistItems") & "&playlistId=" & UploadsPlaylistId & 
                          "&part=snippet,contentDetails&maxResults=50" &
                          (if pageToken <> null then "&pageToken=" & pageToken else ""),
                    json = Json.Document(Web.Contents(url)),
                    items = try json[items] otherwise {},
                    nextToken = try json[nextPageToken] otherwise null
                in
                    [Items = items, NextToken = nextToken, Counter = counter],
            
            // Limit to 50 pages (2500 videos max)
            AllPages = List.Generate(
                () => GetPage(null, 0),
                each [Items] <> null and List.Count([Items]) > 0 and [Counter] < 50,
                each GetPage([NextToken], [Counter] + 1),
                each [Items]
            ),
            
            AllItems = List.Combine(AllPages)
        in
            AllItems,
    
    UploadItems = GetUploadVideos(),
    
    // Convert to table
    UploadsTable = Table.FromList(UploadItems, Splitter.SplitByNothing(), {"Column1"}, null, ExtraValues.Error),
    ExpandedUploads = Table.ExpandRecordColumn(UploadsTable, "Column1", {"snippet", "contentDetails"}),
    ExpandedSnippet = Table.ExpandRecordColumn(ExpandedUploads, "snippet", {"publishedAt"}),
    ExpandedContent = Table.ExpandRecordColumn(ExpandedSnippet, "contentDetails", {"videoId"}),
    
    // Fix date parsing
    AddedDate = Table.TransformColumns(ExpandedContent, {
        {"publishedAt", each try DateTime.FromText(Text.Replace(_, "Z", "")) otherwise DateTime.FromText(_), type datetime}
    }),
    
    // Filter last 2 years
    TwoYearsAgo = DateTime.AddDays(DateTime.LocalNow(), -730),
    FilteredVideos = Table.SelectRows(AddedDate, each [publishedAt] >= TwoYearsAgo),
    
    VideoIdList = FilteredVideos[videoId],
    
    // ========== STEP 3: Get Video Details in Batches ==========
    GetVideoDetails = (videoIds as list) =>
        let
            url = GetApiUrl("videos") & "&id=" & Text.Combine(videoIds, ",") & 
                  "&part=snippet,contentDetails,statistics,liveStreamingDetails",
            json = try Json.Document(Web.Contents(url)) otherwise [items = {}],
            items = try json[items] otherwise {}
        in
            items,
    
    // Create batches of 50
    BatchSize = 50,
    VideoIdBatches = List.Generate(
        () => [i = 0],
        each [i] < List.Count(VideoIdList),
        each [i = [i] + BatchSize],
        each List.FirstN(List.Skip(VideoIdList, [i]), BatchSize)
    ),
    
    // Fetch all batches
    AllVideoDetails = List.Transform(VideoIdBatches, each GetVideoDetails(_)),
    CombinedDetails = List.Combine(AllVideoDetails),
    
    // ========== STEP 4: Transform to Table ==========
    DetailsTable = if List.Count(CombinedDetails) = 0 then
        #table({"Video ID"}, {})
    else
        let
            ToTable = Table.FromList(CombinedDetails, Splitter.SplitByNothing(), {"Column1"}, null, ExtraValues.Error),
            ExpandedDetails = Table.ExpandRecordColumn(ToTable, "Column1", 
                {"id", "snippet", "contentDetails", "statistics", "liveStreamingDetails"}),
            
            // Expand snippet
            ExpandedSnippet2 = Table.ExpandRecordColumn(ExpandedDetails, "snippet", 
                {"title", "description", "publishedAt", "tags", "categoryId", "channelTitle"}),
            
            // Expand contentDetails
            ExpandedContent2 = Table.ExpandRecordColumn(ExpandedSnippet2, "contentDetails", 
                {"duration", "definition"}),
            
            // Expand statistics
            ExpandedStats = Table.ExpandRecordColumn(ExpandedContent2, "statistics", 
                {"viewCount", "likeCount", "commentCount"}),
            
            // Handle liveStreamingDetails (may be null)
            ExpandedLive = try Table.ExpandRecordColumn(ExpandedStats, "liveStreamingDetails", 
                {"actualStartTime", "actualEndTime"}, {"actualStartTime", "actualEndTime"}) 
                otherwise Table.AddColumn(Table.AddColumn(ExpandedStats, "actualStartTime", each null), "actualEndTime", each null),
            
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
            
            // Convert stats to numbers and handle nulls
            ConvertedStats = Table.TransformColumnTypes(AddedVideoType, {
                {"viewCount", Int64.Type},
                {"likeCount", Int64.Type},
                {"commentCount", Int64.Type}
            }),
            
            ReplacedNulls = Table.ReplaceValue(ConvertedStats, null, 0, Replacer.ReplaceValue, 
                {"viewCount", "likeCount", "commentCount"}),
            
            // Add engagement metrics
            AddedEngagement = Table.AddColumn(ReplacedNulls, "Engagement", each 
                [likeCount] + [commentCount], type number),
            
            AddedEngagementRate = Table.AddColumn(AddedEngagement, "Engagement Rate", each 
                if [viewCount] > 0 then Number.Round(([likeCount] + [commentCount]) / [viewCount], 4) else 0, 
                type number),
            
            // Add Tags as text
            AddedTags = Table.AddColumn(AddedEngagementRate, "Tags Text", each 
                if [tags] <> null then Text.Combine([tags], "|") else "", type text),
            
            // Format published date
            FormattedDate = Table.TransformColumns(AddedTags, {
                {"publishedAt", each try DateTime.ToText(DateTime.FromText(_), "yyyy-MM-dd HH:mm:ss") 
                    otherwise DateTime.ToText(_, "yyyy-MM-dd HH:mm:ss"), type text}
            }),
            
            // Add timestamps
            CurrentTime = DateTime.ToText(DateTime.LocalNow(), "yyyy-MM-dd HH:mm:ss"),
            AddedTimestamps = Table.AddColumn(FormattedDate, "First Fetched At", each CurrentTime, type text),
            AddedTimestamps2 = Table.AddColumn(AddedTimestamps, "Last Fetched At", each CurrentTime, type text),
            
            // Add Video URL
            AddedUrl = Table.AddColumn(AddedTimestamps2, "Video URL", each 
                "https://www.youtube.com/watch?v=" & [id], type text),
            
            // Add placeholder for playlists (will add separately)
            AddedPlaylists = Table.AddColumn(AddedUrl, "All Playlists", each null, type nullable text),
            AddedPodcast = Table.AddColumn(AddedPlaylists, "Podcast Name", each null, type nullable text),
            
            // Select and rename columns
            FinalTable = Table.SelectColumns(AddedPodcast, {
                "id", "Video URL", "title", "description", "publishedAt", "Duration (Sec)", "duration",
                "Is Short", "Is Live", "Video Type", "viewCount", "likeCount", "commentCount",
                "Engagement", "Engagement Rate", "Tags Text", "All Playlists", "Podcast Name",
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
                {"categoryId", "Category ID"},
                {"channelTitle", "Channel Title"},
                {"definition", "Definition (HD/SD)"},
                {"actualStartTime", "Live Start"},
                {"actualEndTime", "Live End"}
            })
        in
            RenamedColumns
in
    DetailsTable
