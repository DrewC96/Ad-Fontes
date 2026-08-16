"""
Author metadata for figures appearing in ANF Vol I, keyed by the same
slug the parser produces (slugify(div1 title)) so the two join cleanly.

Dates are traditional/scholarly-consensus approximations - patristic
dating is frequently fuzzy or disputed, noted per-entry where relevant.
`era` values match the `eras` table sort order in schema.sql:
Apostolic Fathers -> Ante-Nicene -> Nicene -> Post-Nicene -> Byzantine.
"""

AUTHORS_META = {
    "clement-of-rome": {
        "name": "Clement of Rome",
        "era": "Apostolic Fathers",
        "birth_year": None,
        "death_year": 99,
        "region": "Rome",
        "bio": (
            "Bishop of Rome, traditionally the third successor to Peter. "
            "Author of the First Epistle to the Corinthians (c. 96 AD), "
            "one of the earliest Christian documents outside the New "
            "Testament canon."
        ),
    },
    "mathetes": {
        "name": "Mathetes",
        "era": "Apostolic Fathers",
        "birth_year": None,
        "death_year": None,
        "region": None,
        "bio": (
            "Pseudonym ('the disciple') of the unknown author of the "
            "Epistle to Diognetus. Not a historical individual's real "
            "name - the work's actual authorship is unresolved."
        ),
    },
    "polycarp": {
        "name": "Polycarp",
        "era": "Apostolic Fathers",
        "birth_year": 69,
        "death_year": 155,
        "region": "Smyrna",
        "bio": (
            "Bishop of Smyrna, disciple of the Apostle John. Author of "
            "the Epistle to the Philippians; his martyrdom account is "
            "one of the earliest detailed Christian martyr narratives."
        ),
    },
    "ignatius": {
        "name": "Ignatius of Antioch",
        "era": "Apostolic Fathers",
        "birth_year": 35,
        "death_year": 108,
        "region": "Antioch",
        "bio": (
            "Bishop of Antioch, martyred in Rome. Author of seven "
            "genuine epistles written en route to his execution; "
            "several additional epistles attributed to him are later "
            "forgeries (the parser separates 'Shorter/Longer/Syriac' "
            "versions and the spurious epistles as distinct works - "
            "worth tagging authenticity in your topic/tags layer)."
        ),
    },
    "barnabas": {
        "name": "Barnabas",
        "era": "Apostolic Fathers",
        "birth_year": None,
        "death_year": None,
        "region": None,
        "bio": (
            "Traditional attribution for the Epistle of Barnabas; "
            "modern scholarship considers the actual author unknown "
            "and likely not the Barnabas of Acts."
        ),
    },
    "papias": {
        "name": "Papias of Hierapolis",
        "era": "Apostolic Fathers",
        "birth_year": 60,   # disputed - estimates range c. 60-70
        "death_year": 130,  # disputed - estimates range c. 130-163
        "region": "Hierapolis",
        "bio": (
            "Bishop of Hierapolis. Only fragments of his work survive, "
            "quoted by later writers (esp. Eusebius). Dates are "
            "genuinely disputed in scholarship - treat as approximate."
        ),
    },
    "justin-martyr": {
        "name": "Justin Martyr",
        "era": "Ante-Nicene",
        "birth_year": 100,
        "death_year": 165,
        "region": "Rome",
        "bio": (
            "Christian apologist and philosopher, martyred in Rome. "
            "Author of the First and Second Apologies and the Dialogue "
            "with Trypho, foundational texts of Christian apologetics."
        ),
    },
    "irenaeus": {
        "name": "Irenaeus of Lyons",
        "era": "Ante-Nicene",
        "birth_year": 130,
        "death_year": 202,
        "region": "Lyons",
        "bio": (
            "Bishop of Lyons, disciple of Polycarp. Author of Against "
            "Heresies, the major early refutation of Gnosticism and a "
            "cornerstone text for apostolic succession and the rule "
            "of faith."
        ),
    },
}
