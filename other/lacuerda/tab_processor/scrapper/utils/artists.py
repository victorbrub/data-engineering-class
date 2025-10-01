import musicbrainzngs

musicbrainzngs.set_useragent("MyApp", "1.0", "myemail@example.com")

result = musicbrainzngs.search_artists(artist="Estopa")
artist_id = result["artist-list"][0]["id"]

artist_info = musicbrainzngs.get_artist_by_id(artist_id, includes=["tags", "releases"])
print(artist_info)
