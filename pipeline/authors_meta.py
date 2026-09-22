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

    # --- ANF Vol II ---
    "hermas": {
        "name": "Hermas",
        "era": "Apostolic Fathers",
        "birth_year": None,
        "death_year": None,
        "region": "Rome",
        "bio": (
            "Traditional author of the Shepherd of Hermas, a widely-read "
            "early Christian text of visions, mandates, and parables. "
            "Identity and exact dating are debated - possibly a brother "
            "of Pope Pius I, or a distinct earlier figure."
        ),
    },
    "tatian": {
        "name": "Tatian",
        "era": "Ante-Nicene",
        "birth_year": 120,
        "death_year": 180,
        "region": "Assyria",
        "bio": (
            "Assyrian Christian apologist, student of Justin Martyr in "
            "Rome. Author of the Address to the Greeks and the "
            "Diatessaron, an early harmony of the four Gospels into a "
            "single narrative. Later associated with the Encratite "
            "movement, which is reflected in some source commentary."
        ),
    },
    "athenagoras": {
        "name": "Athenagoras of Athens",
        "era": "Ante-Nicene",
        "birth_year": 133,
        "death_year": 190,
        "region": "Athens",
        "bio": (
            "Christian apologist and philosopher. Author of A Plea for "
            "the Christians, addressed to Emperor Marcus Aurelius, and "
            "On the Resurrection."
        ),
    },
    "theophilus": {
        "name": "Theophilus of Antioch",
        "era": "Ante-Nicene",
        "birth_year": None,
        "death_year": 185,
        "region": "Antioch",
        "bio": (
            "Bishop of Antioch. Author of To Autolycus, an apologetic "
            "work addressed to a pagan friend, notable for an early use "
            "of the Greek term 'Trias' (Trinity)."
        ),
    },
    "clement-of-alexandria": {
        "name": "Clement of Alexandria",
        "era": "Ante-Nicene",
        "birth_year": 150,
        "death_year": 215,
        "region": "Alexandria",
        "bio": (
            "Head of the Catechetical School of Alexandria. Author of "
            "Exhortation to the Heathen, The Instructor, and the "
            "Stromata (Miscellanies) - foundational works bringing "
            "Greek philosophy into conversation with Christian thought."
        ),
    },

    # --- NPNF Series I (Vols 1-14) ---
    "augustine-of-hippo": {
        "name": "Augustine of Hippo",
        "era": "Post-Nicene",
        "birth_year": 354,
        "death_year": 430,
        "region": "Hippo Regius (North Africa)",
        "bio": (
            "Bishop of Hippo Regius, the most influential Latin Father "
            "of the Church. Author of the Confessions, The City of God, "
            "On Christian Doctrine, and the major anti-Manichaean, "
            "anti-Donatist, and anti-Pelagian treatises collected here "
            "(NPNF Series I, Vols. 1-8) - his writings shaped Western "
            "theology on grace, original sin, the sacraments, and the "
            "nature of the Church more than any other patristic figure."
        ),
    },
    "john-chrysostom": {
        "name": "John Chrysostom",
        "era": "Post-Nicene",
        "birth_year": 349,
        "death_year": 407,
        "region": "Antioch / Constantinople",
        "bio": (
            "Archbishop of Constantinople, called 'Chrysostom' "
            "('golden-mouthed') for his oratory. The most prolific "
            "Greek homilist of the patristic era, represented here "
            "(NPNF Series I, Vols. 9-14) by his extensive homily "
            "cycles on Matthew, John, Acts, Romans, and the Pauline "
            "epistles, alongside treatises like On the Priesthood."
        ),
    },

    # --- NPNF Series II (Vol. 1: Eusebius) ---
    "eusebius-of-caesarea": {
        "name": "Eusebius of Caesarea",
        "era": "Nicene",
        "birth_year": 260,
        "death_year": 340,
        "region": "Caesarea (Palestine)",
        "bio": (
            "Bishop of Caesarea, 'the Father of Church History'. "
            "Author of the Church History (Historia Ecclesiastica), "
            "the principal surviving narrative source for the first "
            "three centuries of Christianity, and the Life of "
            "Constantine, alongside his own panegyric oration in "
            "praise of Constantine (NPNF Series II, Vol. 1)."
        ),
    },
    "constantine-the-great": {
        "name": "Constantine the Great",
        "era": "Nicene",
        "birth_year": 272,
        "death_year": 337,
        "region": "Roman Empire",
        "bio": (
            "Roman Emperor, not a theologian or Church Father, but "
            "included here because NPNF Series II, Vol. 1 preserves "
            "his own Oration to the Assembly of the Saints as a "
            "primary source appended to Eusebius's Life of "
            "Constantine - the oration is Constantine's own "
            "composition, not Eusebius's, so it is attributed to him "
            "directly rather than folded into Eusebius's works."
        ),
    },
    "socrates-scholasticus": {
        "name": "Socrates Scholasticus",
        "era": "Post-Nicene",
        "birth_year": 380,
        "death_year": 439,  # death year uncertain - after 439, exact date unknown
        "region": "Constantinople",
        "bio": (
            "Constantinopolitan lawyer ('scholasticus') and church "
            "historian. Author of the Ecclesiastical History covering "
            "306-439 AD, continuing Eusebius's history down through "
            "the Arian and other 4th/5th-century controversies "
            "(NPNF Series II, Vol. 2)."
        ),
    },
    "sozomen": {
        "name": "Sozomen",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": 450,  # approximate
        "region": "Palestine / Constantinople",
        "bio": (
            "Lawyer and church historian, born in Palestine, active "
            "in Constantinople. Author of an Ecclesiastical History "
            "covering roughly the same period as Socrates "
            "Scholasticus (whose work he knew and partly drew on), "
            "with more attention to monasticism (NPNF Series II, "
            "Vol. 2)."
        ),
    },
    "theodoret-of-cyrus": {
        "name": "Theodoret of Cyrus",
        "era": "Post-Nicene",
        "birth_year": 393,
        "death_year": 457,
        "region": "Cyrus (Syria)",
        "bio": (
            "Bishop of Cyrus, prominent Antiochene theologian and "
            "historian, a central figure in the Nestorian and "
            "Eutychian controversies. Represented here (NPNF Series "
            "II, Vol. 3) by his Ecclesiastical History, the dialogue "
            "Eranistes, his Letters, and his Counter-statements "
            "responding to Cyril of Alexandria's Twelve Anathemas."
        ),
    },
    "jerome": {
        "name": "Jerome",
        "era": "Post-Nicene",
        "birth_year": 347,
        "death_year": 420,
        "region": "Stridon / Bethlehem",
        "bio": (
            "Translator of the Vulgate, biblical scholar, and "
            "polemicist. Represented here (NPNF Series II, Vol. 3) by "
            "his Lives of Illustrious Men (De Viris Illustribus) and "
            "his Apology against Rufinus, written during their bitter "
            "controversy over Origen."
        ),
    },
    "gennadius-of-marseilles": {
        "name": "Gennadius of Marseilles",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": 496,  # approximate
        "region": "Marseilles",
        "bio": (
            "Priest of Marseilles. Continued Jerome's Lives of "
            "Illustrious Men with a further list of ecclesiastical "
            "writers after Jerome's death (NPNF Series II, Vol. 3)."
        ),
    },
    "rufinus-of-aquileia": {
        "name": "Rufinus of Aquileia",
        "era": "Post-Nicene",
        "birth_year": 344,
        "death_year": 411,
        "region": "Aquileia / Palestine",
        "bio": (
            "Monk, translator, and theologian, best known for his "
            "Latin translations of Origen and his continuation of "
            "Eusebius's Church History. Engaged in a bitter public "
            "controversy with his former friend Jerome over Origen's "
            "orthodoxy. Represented here (NPNF Series II, Vol. 3) by "
            "his own Apology, his Commentary on the Apostles' Creed, "
            "and prefatory/appended material to his translations."
        ),
    },
    "anastasius-i-of-rome": {
        "name": "Anastasius I of Rome",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": 401,
        "region": "Rome",
        "bio": (
            "Bishop of Rome (Pope), 399-401. Represented here (NPNF "
            "Series II, Vol. 3) by a single letter to John, Bishop of "
            "Jerusalem, concerning the controversy over Rufinus and "
            "Origen's orthodoxy."
        ),
    },
    "pamphilus-of-caesarea": {
        "name": "Pamphilus of Caesarea",
        "era": "Ante-Nicene",
        "birth_year": 240,
        "death_year": 309,
        "region": "Caesarea (Palestine)",
        "bio": (
            "Priest, scholar, and martyr, teacher and namesake of "
            "Eusebius of Caesarea ('Eusebius Pamphili'). Author of a "
            "Defence (Apology) for Origen, preserved only through "
            "Rufinus's Latin translation - represented here (NPNF "
            "Series II, Vol. 3) as Pamphilus's own composition, "
            "distinct from Rufinus's own appended epilogue to it."
        ),
    },
    "cyril-of-alexandria": {
        "name": "Cyril of Alexandria",
        "era": "Post-Nicene",
        "birth_year": 376,
        "death_year": 444,
        "region": "Alexandria",
        "bio": (
            "Patriarch of Alexandria, central figure of the "
            "Nestorian controversy and the Council of Ephesus (431). "
            "Represented here (NPNF Series II, Vol. 3) by his Twelve "
            "Anathemas against Nestorius, to which Theodoret's "
            "Counter-statements in the same volume directly respond."
        ),
    },
}