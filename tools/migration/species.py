"""Species shown in the migration atlas. `effort` is the GBIF group (class, or order for the whale) used to correct for
where people record wildlife: each cell's count is divided by all records of that class.
Optional `flyways` limits the population centre trails to the named flyways."""

YEARS = "2010,2025"

EFFORT = {"Aves": 212, "Insecta": 216, "Cetacea": 733}

SPECIES = [
    {"key": 9515886, "slug": "barn-swallow", "name": "Barn swallow", "sci": "Hirundo rustica", "effort": "Aves",
     "wiki": "Barn_swallow",
     "journey": "Breeds across the northern hemisphere and spends the northern winter in southern Africa, South America and southern Asia."},
    {"key": 2481784, "slug": "whimbrel", "name": "Whimbrel", "sci": "Numenius phaeopus", "effort": "Aves",
     "wiki": "Eurasian_whimbrel",
     "journey": "Nests on the Arctic tundra and spends the northern winter on coasts from South Africa to Australia and South America."},
    {"key": 2481912, "slug": "white-stork", "name": "White stork", "sci": "Ciconia ciconia", "effort": "Aves",
     "wiki": "White_stork",
     "journey": "Breeds in Europe and western Asia and crosses at Gibraltar and the Bosporus to winter in Africa."},
    {"key": 2480998, "slug": "amur-falcon", "name": "Amur falcon", "sci": "Falco amurensis", "effort": "Aves",
     "wiki": "Amur_falcon",
     "journey": "Breeds in eastern Asia and crosses the Indian Ocean to spend summer in southern Africa, Zimbabwe included."},
    {"key": 5228340, "slug": "woodland-kingfisher", "name": "Woodland kingfisher", "sci": "Halcyon senegalensis", "effort": "Aves",
     "wiki": "Woodland_kingfisher",
     "journey": "An African migrant. It arrives in southern Africa with the November rains and returns north in April."},
    {"key": 2475443, "slug": "european-bee-eater", "name": "European bee-eater", "sci": "Merops apiaster", "effort": "Aves",
     "wiki": "European_bee-eater",
     "journey": "Breeds around the Mediterranean and winters in Africa. Some also breed in South Africa."},
    {"key": 2481681, "slug": "bar-tailed-godwit", "name": "Bar-tailed godwit", "sci": "Limosa lapponica", "effort": "Aves",
     "wiki": "Bar-tailed_godwit",
     "journey": "Breeds on the Arctic tundra. Birds from Alaska fly nonstop to New Zealand in about nine days."},
    {"key": 5228514, "slug": "ruby-throated-hummingbird", "name": "Ruby-throated hummingbird", "sci": "Archilochus colubris", "effort": "Aves",
     "wiki": "Ruby-throated_hummingbird",
     "journey": "Breeds in eastern North America and many cross the Gulf of Mexico in one flight to reach Central America."},
    {"key": 2480562, "slug": "swainsons-hawk", "name": "Swainson's hawk", "sci": "Buteo swainsoni", "effort": "Aves",
     "wiki": "Swainson%27s_hawk",
     "journey": "Breeds on the North American plains and travels in huge flocks to the pampas of Argentina."},
    {"key": 5133088, "slug": "monarch", "name": "Monarch butterfly", "sci": "Danaus plexippus", "effort": "Insecta", "flyways": ["Americas"],
     "wiki": "Monarch_butterfly",
     "journey": "Eastern monarchs fly up to 4,000 km to winter in the mountain forests of central Mexico."},
    {"key": 4299368, "slug": "painted-lady", "name": "Painted lady", "sci": "Vanessa cardui", "effort": "Insecta",
     "wiki": "Vanessa_cardui",
     "journey": "Moves between tropical Africa and Europe over several generations, crossing the Sahara each year."},
    {"key": 5220086, "slug": "humpback-whale", "name": "Humpback whale", "sci": "Megaptera novaeangliae", "effort": "Cetacea",
     "wiki": "Humpback_whale",
     "journey": "Feeds in cold polar waters in summer and travels to warm tropical seas to breed and calve."},
]
