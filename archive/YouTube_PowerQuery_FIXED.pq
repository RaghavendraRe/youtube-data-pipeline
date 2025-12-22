// YouTube Data - Power Query Compatible (No Dynamic URL Issues)
// Paste this into Power BI Desktop > Get Data > Blank Query > Advanced Editor

let
    // --- CONFIGURATION ---
    API_KEY = "AIzaSyBM5DU838aPORBzQE7L3Hv1q7PGSEQlGU", 
    CHANNEL_ID = "UCUDKhNE_Y_DVkFx1nFNZTWQ",
    MAX_PAGES = 50,
    
    // --- HELPER FUNCTIONS ---
    // Use Web.Contents with RelativePath to avoid dynamic URL errors
    GetJson = (endpoint as text, query as text) => 
        Json.Document(
            Web.Contents(
                "https://www.googleapis.com/youtube/v3/",
                [
                    RelativePath = endpoint,
                    Query = [key = API_KEY] & Record.FromList(Text.Split(query, "&"), List.Transform(Text.Split(query, "&"), each Text.BeforeDelimiter(_, "=")))
                ]
            )
        ),
    
    GetJsonSimple = (fullUrl as text) => Json.Document(Web.Contents(fullUrl)),
    
    // Helper to Convert ISO Duration
    IsoToSeconds = (text as any) => 
        if text = null then 0 else
        let
            clean = Text.Replace(text, "PT", ""),
            h = if Text.Contains(clean, "H") then Number.From(Text.BeforeDelimiter(clean, "H")) else 0,
            rem1 = if Text.Contains(clean, "H") then Text.AfterDelimiter(clean, "H") else clean,
            m = if Text.Contains(rem1, "M") then Number.From(Text.BeforeDelimiter(rem1, "M")) else 0,
            rem2 = if Text.Contains(rem1, "M") then Text.AfterDelimiter(rem1, "M") else rem1,
            s = if Text.Contains(rem2, "S") then Number.From(Text.Remove(Text.BeforeDelimiter(rem2, "S"), "S")) else 0
        in
            (h * 3600) + (m * 60) + s,

    // 1. Get Uploads ID (Using fixed base URL)
    ChannelData = Json.Document(
        Web.Contents(
            "https://www.googleapis.com/youtube/v3/channels",
            [
                Query = [
                    part = "contentDetails",
                    id = CHANNEL_ID,
                    key = API_KEY
                ]
            ]
        )
    ),
    UploadsId = ChannelData[items]{0}[contentDetails][relatedPlaylists][uploads],

    // 2. Fetch Video IDs with Pagination
    GetPlaylistPage = (pageToken as nullable text) =>
        let
            QueryRecord = if pageToken = null then
                [
                    part = "contentDetails",
                    maxResults = "50",
                    playlistId = UploadsId,
                    key = API_KEY
                ]
            else
                [
                    part = "contentDetails",
                    maxResults = "50",
                    playlistId = UploadsId,
                    key = API_KEY,
                    pageToken = pageToken
                ],
            Data = Json.Document(
                Web.Contents(
                    "https://www.googleapis.com/youtube/v3/playlistItems",
                    [Query = QueryRecord]
                )
            )
        in
            Data,
    
    Source = List.Generate(
        () => [Result = GetPlaylistPage(null), Counter = 0],
        each [Result][items] <> null and [Counter] < MAX_PAGES,
        each [
            NextToken = try [Result][nextPageToken] otherwise null,
            Counter = [Counter] + 1,
            Result = GetPlaylistPage(NextToken)
        ],
        each [Result][items]
    ),
    
    // Flatten to Table
    TableSource = Table.FromList(Source, Splitter.SplitByNothing(), {"Column1"}, null, ExtraValues.Error),
    ExpandedList = Table.ExpandListColumn(TableSource, "Column1"),
    ExpandedContent = Table.ExpandRecordColumn(ExpandedList, "Column1", {"contentDetails"}),
    ExpandedVideoId = Table.ExpandRecordColumn(ExpandedContent, "contentDetails", {"videoId", "videoPublishedAt"}, {"VideoID", "Published Date"}),

    // 3. Get Video Details (Using fixed base URL)
    GetDetails = (vid as text) =>
        let
            Data = Json.Document(
                Web.Contents(
                    "https://www.googleapis.com/youtube/v3/videos",
                    [
                        Query = [
                            part = "snippet,statistics,contentDetails,liveStreamingDetails",
                            id = vid,
                            key = API_KEY
                        ]
                    ]
                )
            ),
            Item = try Data[items]{0} otherwise null,
            Res = if Item = null then [] else [
                Title = Item[snippet][title],
                Description = Item[snippet][description],
                TagsList = try Item[snippet][tags] otherwise {}, 
                CategoryId = Item[snippet][categoryId],
                ChannelTitle = Item[snippet][channelTitle],
                Views = try Number.From(Item[statistics][viewCount]) otherwise 0,
                Likes = try Number.From(Item[statistics][likeCount]) otherwise 0,
                Comments = try Number.From(Item[statistics][commentCount]) otherwise 0,
                DurationISO = Item[contentDetails][duration],
                Definition = Item[contentDetails][definition],
                LiveStart = try Item[liveStreamingDetails][actualStartTime] otherwise null,
                LiveEnd = try Item[liveStreamingDetails][actualEndTime] otherwise null
            ]
        in
            Res,

    // Apply Function
    AddedDetails = Table.AddColumn(ExpandedVideoId, "Details", each GetDetails([VideoID])),
    ExpandedDetails = Table.ExpandRecordColumn(AddedDetails, "Details", 
        {"Title", "Description", "TagsList", "CategoryId", "ChannelTitle", "Views", "Likes", "Comments", "DurationISO", "Definition", "LiveStart", "LiveEnd"}
    ),

    // 4. Calculations
    TagsToString = Table.AddColumn(ExpandedDetails, "Tags", each Text.Combine([TagsList], "|")),
    DurationSec = Table.AddColumn(TagsToString, "Duration (Sec)", each IsoToSeconds([DurationISO])),
    IsShort = Table.AddColumn(DurationSec, "Is Short", each if [#"Duration (Sec)"] <= 60 and [#"Duration (Sec)"] > 0 then true else false),
    IsLive = Table.AddColumn(IsShort, "Is Live", each if [LiveStart] <> null then true else false),
    VideoType = Table.AddColumn(IsLive, "Video Type", each if [Is Live] then "Live" else if [Is Short] then "Short" else "Long"),
    Engagement = Table.AddColumn(VideoType, "Engagement", each [Likes] + [Comments]),
    EngagementRate = Table.AddColumn(Engagement, "Engagement Rate", each if [Views] > 0 then [Engagement] / [Views] else 0),
    VideoUrl = Table.AddColumn(EngagementRate, "Video URL", each "https://www.youtube.com/watch?v=" & [VideoID]),

    // 5. Add columns for playlists
    AllPlaylist = Table.AddColumn(VideoUrl, "All Playlists", each null, type nullable text),
    PodcastName = Table.AddColumn(AllPlaylist, "Podcast Name", each null, type nullable text),
    
    // Add timestamps
    CurrentTime = DateTime.ToText(DateTime.LocalNow(), "yyyy-MM-dd HH:mm:ss"),
    FirstFetched = Table.AddColumn(PodcastName, "First Fetched At", each CurrentTime, type text),
    LastFetched = Table.AddColumn(FirstFetched, "Last Fetched At", each CurrentTime, type text),

    // Final Selection and Rename
    FinalTable = Table.SelectColumns(LastFetched, {
        "VideoID", "Video URL", "Title", "Description", "Published Date", 
        "Duration (Sec)", "DurationISO", "Is Short", "Is Live", "Video Type",
        "Views", "Likes", "Comments", "Engagement", "Engagement Rate",
        "Tags", "All Playlists", "Podcast Name", "CategoryId", "ChannelTitle", 
        "Definition", "LiveStart", "LiveEnd", "First Fetched At", "Last Fetched At"
    }),
    
    RenamedColumns = Table.RenameColumns(FinalTable, {
        {"VideoID", "Video ID"},
        {"DurationISO", "Duration (ISO)"},
        {"CategoryId", "Category ID"},
        {"ChannelTitle", "Channel Title"},
        {"Definition", "Definition (HD/SD)"},
        {"LiveStart", "Live Start"},
        {"LiveEnd", "Live End"}
    }),
    
    TypedTable = Table.TransformColumnTypes(RenamedColumns, {
        {"Views", Int64.Type}, {"Likes", Int64.Type}, {"Comments", Int64.Type}, 
        {"Engagement", Int64.Type}, {"Engagement Rate", type number}, 
        {"Published Date", type datetime}, {"Live Start", type datetime}, {"Live End", type datetime},
        {"Is Short", type logical}, {"Is Live", type logical}, {"Duration (Sec)", Int64.Type}
    })
in
    TypedTable
