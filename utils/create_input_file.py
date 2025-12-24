import pandas as pd
import os

# Raw data from user
data_raw = [
    # Category, Name (Inferred), URL, Channel ID
    ("BK Hindi", "Administration Wing", "https://youtube.com/@administrationwing5085?si=fACb3JclexWJ6YoY", "UCUDKhNE_Y_DVkFx1nFNZTWQ"),
    
    ("Wings", "Administration Wing", "https://youtube.com/@administrationwing5085?si=fACb3JclexWJ6YoY", "UCUpMVT28UD4sStVOXagHUug"),
    ("Wings", "Yogic Kheti", "https://youtube.com/@yogickheti?si=oVD4_G6ncVeKjzMQ", "UC30NvyZjRmdrLvsZ3VFEHpQ"),
    ("Wings", "BK Art Wing", "https://youtube.com/@bkartwing?si=LFNTSP5lUQyoWQlh", "UCjH-o05YhKvJFfD5fR0pnJA"),
    ("Wings", "Business & Industry Wing", "https://youtube.com/@businessindustrywing-rerf-4?si=C38CbKZsxFifeAzO", "UC6Ym9WLXxzV2tDCj39zorUg"),
    ("Wings", "Education Wing", "https://youtube.com/@educationwingrerf?si=ACwvjOSRs2Vy7ZcA", "UCFACN6E_0gRsDlk9Zzd31WQ"),
    ("Wings", "BK IT Wing", "https://youtube.com/@bkitwing?si=C9tCl5ut94HtEEFg", "UCYCAYFgoaBn8vzRYXHuTZiA"),
    ("Wings", "BK Jurists Wing", "https://youtube.com/@bkjuristswing?si=Apr-fJjnky214Jds", "UCkX16g5aVEcp9hQOAaUJ1aw"),
    ("Wings", "BK Media Wing", "https://youtube.com/@bkmediawing?si=UxAJXvTTZ_0d5cR7", "UC7U65334H-ddTZbGu0kTvZg"),
    ("Wings", "BK Medical Wing", "https://youtube.com/@bkmedicalwing1?si=oDqjiSHBGPhIpL7h", "UCYJrPmZ8Pv5We-u7Pbo68VQ"),
    ("Wings", "BK Security Wing", "https://youtube.com/@bksecuritywing?si=QyDNf0L68FinKeu8", "UCUxekvzpEVR9r78vxYNOGKg"),
    ("Wings", "Say Wing", "https://youtube.com/@satwing-rerf-brahmakumaris2718?si=Zy30Ahj2HOEs9yEK", "UC9SQoGGuMIUuPH1tQT5Fe3A"),
    ("Wings", "BK Social Wing", "https://youtube.com/@bksocialwing?si=M5HDX2nk2zsFGIPP", "UCJrtJX9R241PFJQ7dPeVK_A"),
    ("Wings", "Sparc Wing", "https://youtube.com/@sparcwingmadhuban?si=vAtVH3u_INmwdT-Z", "UCikH6f53KZvK-hats6hFJtg"),
    ("Wings", "Sports Wing", "https://youtube.com/@sportswingbrahmakumaris?si=cOZPTV2HjlqjPeRH", "UCa9Rk4piNuVvHTHXfmcFLxg"),
    ("Wings", "Transport Wing", "https://youtube.com/@brahmakumaristransportwing?si=agq4MrXTjI8PofGZ", "UCig17vCFDNYMmxq-Raa_aSQ"),
    ("Wings", "BK Women Wing", "https://youtube.com/@bkwomenwing?si=7mYveTUEx95qr0zW", "UCBLmKtSV3vftCXa2F7V9VSw"),
    ("Wings", "Youth Wing", "https://youtube.com/@youthwingbrahmakumaris?si=JBfk8W5Xd97FSVpG", "UCPoZwj8IidJL6mB_0q8p5SQ"),

    ("Seva", "BK DI Wing", "https://youtube.com/@bkdiwing?si=FVdWSf3oJN_9J-os", "UCB6jer7WUM1J_s5tSGQuW3g"),

    ("TV Media", "Awakening TV", "https://youtube.com/@awakeningtv?si=XwDAZCz8KX3PJ1DB", "UCQ8kxAu_on_YzVPMjB03rqA"),
    ("TV Media", "Peace of Mind TV", "https://youtube.com/@tvpeaceofmind?si=rcFRlyNsoNjABP20", "UCmw4wZ3FRso2TsS36FQ6heA"),
    ("TV Media", "Godlywood Studio", "https://youtube.com/@godlywoodstudio?si=UAibDhMCz1Bvyy53", "UCtex25LnQET78C1bNqNuThg"),
    ("TV Media", "Om Shanti Channel", "https://youtube.com/@omshantichannelgws?si=8q2OsF7lQLU-A6i1", "UCUcvsN9Jqc4RzVvMlJ1y_FA"),
    ("TV Media", "Om Shanti Musics", "https://youtube.com/@omshantimusics?si=WSIxJiWIbFN5Si_N", "UCHlv3wd98vwjY2IemIFIqnA"),
    ("TV Media", "Brahma Kumaris Music", "https://youtube.com/@brahmakumarismusic?si=Kjbdfl0DcZHYpxWY", "UCmjhViJ2f2WZQEle9C3pLMQ"),
    ("TV Media", "Brahma Kumaris News", "https://youtube.com/@brahmakumarisnews?si=AfXeArMngky5t7Hq", "UC1WIjZOzvc7KJqgrl167UTg"),
    ("TV Media", "Brahma Kumaris Events", "https://youtube.com/@brahmakumarisevents?si=2TS_-KjRMLDfGaYg", "UC3RjCO_9LLJmUEy-XPHRVew"),

    ("Radios", "Radio Madhuban", "https://youtube.com/@fmradiomadhuban?si=1MwaJPkRKwscPfvX", "UCpIa1Enmbrv3bWsiGd9Sg-w"),
    ("Radios", "Radio Sabarmati", "https://youtube.com/@radiosabarmati?si=Cwd95Y0CvkxlS1Bn", "UCkrT7Ja2BcxK1zq-gayr_JQ"),
    ("Radios", "Radio Manjeera", "https://youtube.com/@radiomanjeera710?si=VM9ji44GYirBj8Yl", "UC08Vfh2wUPYYwEAgN0R1r3w"),
    ("Radios", "Puneri Awaz", "https://youtube.com/@puneriawaz?si=SNnVnNApURpP8VOw", "UC7twd1VXDGkYPJ75T8GhVJA"),

    ("Academy", "Gyan Sarovar Academy", "https://youtube.com/@gyansarovaracademy?si=KWRIMEu0LQK-RNfC", "UCrn6wFv6_rxhddXl9ayRDNg"),

    ("BK Tamil", "Brahma Kumaris TN", "https://youtube.com/@brahmakumaristn?si=ufi_g1Vaf969Vmz3", "UCYfMGhyXN9laRF2CgDlrOMQ"),

    ("Rajyog Teachers", "BK Jayanti", "https://youtube.com/@bkjayanti?si=E6cZpOTQSSVZ4_EY", "UCHfL72eSMt3EOUj_c8-pWgw"),
    ("Rajyog Teachers", "BK Shivani", "https://youtube.com/@bkshivani?si=fnPkMgWexKAEsNj-", "UCQdyCrZpGq4Bbu6V8LPUDWg"),
    ("Rajyog Teachers", "BK Usha", "https://youtube.com/@bkushamadhuban?si=IsJboYW9Rh1CiDWJ", "UCbldwxotHkXXtUYoC0jzVTw"),
    ("Rajyog Teachers", "BK Geeta", "https://youtube.com/@bkgeeta?si=dc0OPjLCowhQnEgI", "UC_bcel8eUG80Sk5ZW5IvHUw"),
    ("Rajyog Teachers", "BK Raju", "https://youtube.com/@bkraju?si=nahoxstEDRAM8uS7", "UCdjxb7P0G7p9pMBWEiBwlLA"),
    ("Rajyog Teachers", "BK Brijmohan", "https://youtube.com/@bkbrijmohan?si=K3wcrrTuU10x919-", "UCFVaWOVSE9dO8q8U8f_pXow")
]

# Convert to DataFrame
df = pd.DataFrame(data_raw, columns=["Wing", "Entity Name", "URL", "Channel ID"])

# Save to Excel
OUTPUT_PATH = "data/handles_list.xlsx"
df.to_excel(OUTPUT_PATH, index=False)

print(f"✅ Successfully created {OUTPUT_PATH} with {len(df)} channels.")
print(df.head())
