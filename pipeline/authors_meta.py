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
    "athanasius-of-alexandria": {
        "name": "Athanasius of Alexandria",
        "era": "Nicene",
        "birth_year": 296,
        "death_year": 373,
        "region": "Alexandria",
        "bio": (
            "Bishop of Alexandria, present at Nicaea (325) as a young "
            "deacon and the leading defender of Nicene orthodoxy "
            "through decades of Arian controversy and repeated exile. "
            "Represented here (NPNF Series II, Vol. 4) by his major "
            "anti-Arian works (Contra Gentes, De Incarnatione, "
            "Orationes contra Arianos), the Life of Antony, his "
            "apologetic writings, and his Festal and Personal Letters."
        ),
    },
    "eusebius-of-nicomedia": {
        "name": "Eusebius of Nicomedia",
        "era": "Nicene",
        "birth_year": None,
        "death_year": 341,
        "region": "Nicomedia / Constantinople",
        "bio": (
            "Bishop of Nicomedia, later Constantinople - a leading "
            "Arian sympathizer and political opponent of Athanasius, "
            "distinct from Eusebius of Caesarea. Represented here "
            "(NPNF Series II, Vol. 4) by a single letter preserved "
            "and quoted within Athanasius's own writing against him."
        ),
    },
    "author-of-the-historia-acephala": {
        "name": "Author of the Historia Acephala",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Alexandria (Egypt)",
        "bio": (
            "Unknown compiler of the Historia Acephala ('headless "
            "history' - its opening is lost), an anonymous ancient "
            "chronicle of events in Athanasius's episcopate. Not "
            "written by Athanasius himself; preserved alongside his "
            "own letters (NPNF Series II, Vol. 4) as a historical "
            "source about him rather than by him."
        ),
    },

    # --- NPNF Series II, Vols. 5-13 ---
    "gregory-of-nyssa": {
        "name": "Gregory of Nyssa",
        "era": "Post-Nicene",
        "birth_year": 335,  # approximate
        "death_year": 395,  # approximate
        "region": "Cappadocia (Nyssa)",
        "bio": (
            "Bishop of Nyssa, younger brother of Basil of Caesarea and "
            "one of the three Cappadocian Fathers, the most speculative "
            "theologian of the three. Represented here (NPNF Series II, "
            "Vol. 5) by Against Eunomius, the Great Catechism, On the "
            "Making of Man, and On the Soul and the Resurrection."
        ),
    },
    "basil-of-caesarea": {
        "name": "Basil of Caesarea",
        "era": "Post-Nicene",
        "birth_year": 330,  # approximate
        "death_year": 379,
        "region": "Cappadocia (Caesarea)",
        "bio": (
            "Bishop of Caesarea, 'Basil the Great', a leading defender "
            "of Nicene orthodoxy and the organizer of Eastern monastic "
            "life. Represented here (NPNF Series II, Vol. 8) by On the "
            "Holy Spirit, the Hexaemeron, and his Letters."
        ),
    },
    "cyril-of-jerusalem": {
        "name": "Cyril of Jerusalem",
        "era": "Post-Nicene",
        "birth_year": 313,  # approximate
        "death_year": 386,
        "region": "Jerusalem",
        "bio": (
            "Bishop of Jerusalem, best known for his Catechetical "
            "Lectures (c. 350), instructions for baptismal candidates "
            "that are a major witness to fourth-century doctrine and "
            "liturgy (NPNF Series II, Vol. 7)."
        ),
    },
    "gregory-of-nazianzus": {
        "name": "Gregory of Nazianzus",
        "era": "Post-Nicene",
        "birth_year": 329,  # approximate
        "death_year": 390,
        "region": "Nazianzus / Constantinople",
        "bio": (
            "'Gregory the Theologian', Cappadocian Father and briefly "
            "Archbishop of Constantinople, famed for his Theological "
            "Orations on the Trinity. Represented here (NPNF Series "
            "II, Vol. 7) by select Orations and Letters."
        ),
    },
    "john-of-damascus": {
        "name": "John of Damascus",
        "era": "Byzantine",
        "birth_year": 675,  # approximate
        "death_year": 749,
        "region": "Damascus / Mar Saba (Palestine)",
        "bio": (
            "Monk and theologian, often called the last of the Greek "
            "Fathers. Author of An Exact Exposition of the Orthodox "
            "Faith, a systematic summary of Greek patristic doctrine "
            "(NPNF Series II, Vol. 9)."
        ),
    },
    "ambrose-of-milan": {
        "name": "Ambrose of Milan",
        "era": "Post-Nicene",
        "birth_year": 340,  # approximate
        "death_year": 397,
        "region": "Milan",
        "bio": (
            "Bishop of Milan, teacher of Augustine, and one of the four "
            "original Latin Doctors of the Church. Represented here "
            "(NPNF Series II, Vol. 10) by On the Duties of the Clergy, "
            "On the Holy Spirit, his sacramental and ascetic treatises, "
            "and selected Letters."
        ),
    },
    "symmachus": {
        "name": "Symmachus",
        "era": "Post-Nicene",
        "birth_year": 345,  # approximate
        "death_year": 402,
        "region": "Rome",
        "bio": (
            "Quintus Aurelius Symmachus, pagan senator and Prefect of "
            "Rome. Not a Christian writer: included as the author of "
            "the Memorial asking Emperor Valentinian II to restore the "
            "Altar of Victory, which Ambrose answered and whose text is "
            "preserved in Ambrose's correspondence (NPNF Series II, "
            "Vol. 10)."
        ),
    },
    "sulpitius-severus": {
        "name": "Sulpitius Severus",
        "era": "Post-Nicene",
        "birth_year": 363,  # approximate
        "death_year": 425,  # approximate
        "region": "Aquitaine (Gaul)",
        "bio": (
            "Aristocrat turned ascetic and biographer of Martin of "
            "Tours. Author of the Life of St. Martin, the Dialogues, "
            "and the Sacred History (NPNF Series II, Vol. 11)."
        ),
    },
    "vincent-of-lerins": {
        "name": "Vincent of Lerins",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": 445,  # approximate
        "region": "Lerins (Gaul)",
        "bio": (
            "Monk of the island monastery of Lerins. Author of the "
            "Commonitory (434), source of the 'Vincentian Canon', the "
            "test of catholic faith as what has been believed "
            "everywhere, always, and by all (NPNF Series II, Vol. 11)."
        ),
    },
    "john-cassian": {
        "name": "John Cassian",
        "era": "Post-Nicene",
        "birth_year": 360,  # approximate
        "death_year": 435,  # approximate
        "region": "Marseilles (Gaul)",
        "bio": (
            "Monk who carried the ascetic teaching of the Egyptian "
            "desert to the Latin West. Author of the Institutes, the "
            "Conferences, and On the Incarnation of the Lord, Against "
            "Nestorius (NPNF Series II, Vol. 11)."
        ),
    },
    "leo-the-great": {
        "name": "Leo the Great",
        "era": "Post-Nicene",
        "birth_year": 400,  # approximate
        "death_year": 461,
        "region": "Rome",
        "bio": (
            "Bishop of Rome 440-461. His Tome (449) shaped the "
            "Christological definition of the Council of Chalcedon. "
            "Represented here (NPNF Series II, Vol. 12) by his Letters "
            "and Sermons."
        ),
    },
    "gregory-the-great": {
        "name": "Gregory the Great",
        "era": "Post-Nicene",
        "birth_year": 540,  # approximate
        "death_year": 604,
        "region": "Rome",
        "bio": (
            "Bishop of Rome 590-604, traditionally counted among the "
            "four original Latin Doctors of the Church. Represented "
            "here (NPNF Series II, Vols. 12-13) by the Book of "
            "Pastoral Rule and his Register of Epistles."
        ),
    },
    "ephrem-the-syrian": {
        "name": "Ephrem the Syrian",
        "era": "Nicene",
        "birth_year": 306,  # approximate
        "death_year": 373,
        "region": "Nisibis / Edessa (Syria)",
        "bio": (
            "Deacon and hymnographer, the greatest poet of the "
            "Syriac-speaking church. Represented here (NPNF Series II, "
            "Vol. 13) by selected hymns and homilies; his works were "
            "composed in Syriac."
        ),
    },
    "aphrahat": {
        "name": "Aphrahat",
        "era": "Nicene",
        "birth_year": 270,  # approximate
        "death_year": 345,  # approximate
        "region": "Persian Empire (Mesopotamia)",
        "bio": (
            "'The Persian Sage', the earliest Syriac Christian author "
            "whose works survive. Author of twenty-three Demonstrations "
            "written between 337 and 345 (selections in NPNF Series II, "
            "Vol. 13); composed in Syriac."
        ),
    },

    # --- NPNF Series II, Vol. 14: the Seven Ecumenical Councils ---
    # Pseudo-authors for conciliar/canon-law material with no individual
    # human author - one per specific council, per the chosen convention
    # of historical precision over a single generic catch-all.
    "first-council-of-nicaea-325": {
        "name": "First Council of Nicaea (325)",
        "era": "Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Nicaea (Bithynia)",
        "bio": (
            "The first ecumenical council, convened by Constantine. "
            "Produced the Nicene Creed and twenty canons. Represented "
            "here (NPNF Series II, Vol. 14) by the Creed, Canons, and "
            "Synodal Letter."
        ),
    },
    "council-of-ancyra-314": {
        "name": "Council of Ancyra (314)",
        "era": "Ante-Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Ancyra (Galatia)",
        "bio": (
            "Regional council addressing the reconciliation of those who "
            "had lapsed under the Diocletianic persecution. Its canons "
            "were later received by the ecumenical councils (NPNF Series "
            "II, Vol. 14)."
        ),
    },
    "council-of-neocaesarea-315": {
        "name": "Council of Neocaesarea (315)",
        "era": "Ante-Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Neocaesarea (Pontus)",
        "bio": (
            "Regional council on clerical discipline, close in date to "
            "Ancyra. Its canons were later received by the ecumenical "
            "councils (NPNF Series II, Vol. 14)."
        ),
    },
    "council-of-gangra-340": {
        "name": "Council of Gangra (340)",
        "era": "Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Gangra (Paphlagonia)",
        "bio": (
            "Regional council condemning the extreme asceticism of "
            "Eustathius of Sebaste. Its canons were later received by "
            "the ecumenical councils (NPNF Series II, Vol. 14)."
        ),
    },
    "synod-of-antioch-341": {
        "name": "Synod of Antioch (341)",
        "era": "Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Antioch (Syria)",
        "bio": (
            "Council held at the dedication of the 'Golden Church' in "
            "Antioch. Its canons on ecclesiastical order were later "
            "received by the ecumenical councils (NPNF Series II, "
            "Vol. 14)."
        ),
    },
    "council-of-laodicea-363": {
        "name": "Council of Laodicea (363)",
        "era": "Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Laodicea (Phrygia)",
        "bio": (
            "Regional council producing sixty canons on church order and "
            "liturgy, later received by the ecumenical councils (NPNF "
            "Series II, Vol. 14)."
        ),
    },
    "council-of-sardica-343": {
        "name": "Council of Sardica (343)",
        "era": "Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Sardica (Dacia)",
        "bio": (
            "Council called to resolve the split between Eastern and "
            "Western bishops over Athanasius, ending in two rival "
            "sessions. Its Western canons were later received by the "
            "ecumenical councils (NPNF Series II, Vol. 14)."
        ),
    },
    "council-of-carthage-under-cyprian-256": {
        "name": "Council of Carthage under Cyprian (256)",
        "era": "Ante-Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Carthage (North Africa)",
        "bio": (
            "Council presided over by Cyprian of Carthage, on the "
            "rebaptism of heretics. Distinct from the later Council of "
            "Carthage of 419 (NPNF Series II, Vol. 14)."
        ),
    },
    "council-of-constantinople-under-nectarius-394": {
        "name": "Council of Constantinople under Nectarius (394)",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Constantinople",
        "bio": (
            "Regional council held under Patriarch Nectarius, its canon "
            "later received by the ecumenical councils (NPNF Series II, "
            "Vol. 14)."
        ),
    },
    "first-council-of-constantinople-381": {
        "name": "First Council of Constantinople (381)",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Constantinople",
        "bio": (
            "The second ecumenical council, expanding the Nicene Creed "
            "and condemning residual Arianism and Macedonianism. "
            "Represented here (NPNF Series II, Vol. 14) by its Creed, "
            "Canons, and Synodical Letter."
        ),
    },
    "council-of-ephesus-431": {
        "name": "Council of Ephesus (431)",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Ephesus",
        "bio": (
            "The third ecumenical council, condemning Nestorius and "
            "affirming Mary as Theotokos. Represented here (NPNF Series "
            "II, Vol. 14) by its Acts, Decree, and Canons - distinct "
            "from the individual letters of Cyril and Celestine I "
            "preserved alongside them."
        ),
    },
    "council-of-carthage-419": {
        "name": "Council of Carthage (419)",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Carthage (North Africa)",
        "bio": (
            "African council compiling the Code of Canons of the "
            "African Church from earlier African councils. Distinct "
            "from the 256 Council of Carthage under Cyprian (NPNF "
            "Series II, Vol. 14)."
        ),
    },
    "council-of-chalcedon-451": {
        "name": "Council of Chalcedon (451)",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Chalcedon",
        "bio": (
            "The fourth ecumenical council, defining Christ's two "
            "natures against both Nestorianism and Eutychianism. "
            "Represented here (NPNF Series II, Vol. 14) by its Acts, "
            "Definition of Faith, and Canons - distinct from Leo the "
            "Great's Tome and Cyril's letters preserved alongside them."
        ),
    },
    "second-council-of-constantinople-553": {
        "name": "Second Council of Constantinople (553)",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": None,
        "region": "Constantinople",
        "bio": (
            "The fifth ecumenical council, condemning the 'Three "
            "Chapters' and reaffirming Chalcedon. Represented here "
            "(NPNF Series II, Vol. 14) by its Acts, Sentence, and "
            "Capitula - distinct from Emperor Justinian's own "
            "Anathemas against Origen and Pope Vigilius's Decretal "
            "Letter preserved alongside them."
        ),
    },
    "third-council-of-constantinople-680": {
        "name": "Third Council of Constantinople (680)",
        "era": "Byzantine",
        "birth_year": None,
        "death_year": None,
        "region": "Constantinople",
        "bio": (
            "The sixth ecumenical council, condemning Monothelitism. "
            "Represented here (NPNF Series II, Vol. 14) by its Acts and "
            "Definition of Faith - distinct from Pope Agatho's own "
            "Letters preserved alongside them."
        ),
    },
    "council-in-trullo-692": {
        "name": "Council in Trullo (692)",
        "era": "Byzantine",
        "birth_year": None,
        "death_year": None,
        "region": "Constantinople",
        "bio": (
            "The 'Quinisext Council', completing the disciplinary work "
            "of the fifth and sixth ecumenical councils with 102 canons "
            "(NPNF Series II, Vol. 14)."
        ),
    },
    "second-council-of-nicaea-787": {
        "name": "Second Council of Nicaea (787)",
        "era": "Byzantine",
        "birth_year": None,
        "death_year": None,
        "region": "Nicaea (Bithynia)",
        "bio": (
            "The seventh ecumenical council, restoring the veneration "
            "of icons after the first period of Iconoclasm. Represented "
            "here (NPNF Series II, Vol. 14) by its Acts, Decree, and "
            "Canons."
        ),
    },

    # --- Individual authors of letters preserved within Vol. 14 ---
    "celestine-i-of-rome": {
        "name": "Celestine I of Rome",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": 432,
        "region": "Rome",
        "bio": (
            "Bishop of Rome, 422-432. His letter to the Council of "
            "Ephesus (431) supported Cyril of Alexandria against "
            "Nestorius (NPNF Series II, Vol. 14)."
        ),
    },
    "vigilius-of-rome": {
        "name": "Vigilius of Rome",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": 555,
        "region": "Rome",
        "bio": (
            "Bishop of Rome, 537-555. His Decretal Letter confirmed the "
            "acts of the Second Council of Constantinople (553) (NPNF "
            "Series II, Vol. 14)."
        ),
    },
    "agatho-of-rome": {
        "name": "Agatho of Rome",
        "era": "Byzantine",
        "birth_year": None,
        "death_year": 681,
        "region": "Rome",
        "bio": (
            "Bishop of Rome, 678-681. His letters to the Third Council "
            "of Constantinople (680-681) condemned Monothelitism (NPNF "
            "Series II, Vol. 14)."
        ),
    },
    "justinian-i": {
        "name": "Justinian I",
        "era": "Post-Nicene",
        "birth_year": 482,
        "death_year": 565,
        "region": "Constantinople",
        "bio": (
            "Byzantine Emperor, 527-565. Not a theologian or Church "
            "Father, but included here for his own Anathemas against "
            "Origen, issued around the time of the Second Council of "
            "Constantinople (553) and distinct from the council's own "
            "conciliar Anathemas (NPNF Series II, Vol. 14)."
        ),
    },
    "dionysius-of-alexandria": {
        "name": "Dionysius of Alexandria",
        "era": "Ante-Nicene",
        "birth_year": None,
        "death_year": 264,
        "region": "Alexandria",
        "bio": (
            "Bishop of Alexandria, pupil of Origen. His canonical letter "
            "to Basilides on questions of church discipline was later "
            "received as canon law (NPNF Series II, Vol. 14)."
        ),
    },
    "peter-of-alexandria": {
        "name": "Peter of Alexandria",
        "era": "Ante-Nicene",
        "birth_year": None,
        "death_year": 311,
        "region": "Alexandria",
        "bio": (
            "Bishop of Alexandria, martyred under Maximin Daia. His "
            "canons on the treatment of those who lapsed during "
            "persecution, drawn from his Sermon on Penitence, were "
            "later received as canon law (NPNF Series II, Vol. 14)."
        ),
    },
    "gregory-thaumaturgus": {
        "name": "Gregory Thaumaturgus",
        "era": "Ante-Nicene",
        "birth_year": 213,  # approximate
        "death_year": 270,  # approximate
        "region": "Neocaesarea (Pontus)",
        "bio": (
            "Bishop of Neocaesarea, 'the Wonder-Worker', pupil of "
            "Origen. His canonical letter on the treatment of those who "
            "suffered during barbarian raids was later received as "
            "canon law (NPNF Series II, Vol. 14)."
        ),
    },
    "amphilochius-of-iconium": {
        "name": "Amphilochius of Iconium",
        "era": "Post-Nicene",
        "birth_year": 339,  # approximate
        "death_year": 394,  # approximate
        "region": "Iconium",
        "bio": (
            "Bishop of Iconium, cousin and close associate of Gregory "
            "of Nazianzus. Represented here (NPNF Series II, Vol. 14) "
            "by a canonical fragment on which books of Scripture should "
            "be read."
        ),
    },
    "timothy-of-alexandria": {
        "name": "Timothy of Alexandria",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": 385,
        "region": "Alexandria",
        "bio": (
            "Bishop of Alexandria, 380-385, one of the 150 Fathers of "
            "the First Council of Constantinople. His canonical answers "
            "on questions of clerical discipline were later received as "
            "canon law (NPNF Series II, Vol. 14)."
        ),
    },
    "theophilus-of-alexandria": {
        "name": "Theophilus of Alexandria",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": 412,
        "region": "Alexandria",
        "bio": (
            "Bishop of Alexandria, 385-412, uncle of Cyril of "
            "Alexandria. Several of his canonical letters on liturgical "
            "and disciplinary questions were later received as canon "
            "law (NPNF Series II, Vol. 14)."
        ),
    },
    "gennadius-of-constantinople": {
        "name": "Gennadius of Constantinople",
        "era": "Post-Nicene",
        "birth_year": None,
        "death_year": 471,
        "region": "Constantinople",
        "bio": (
            "Patriarch of Constantinople, 458-471. Distinct from "
            "Gennadius of Marseilles (NPNF Series II, Vol. 3). His "
            "encyclical letter on simony was later received as canon "
            "law (NPNF Series II, Vol. 14)."
        ),
    },
    "apostolic-canons-anonymous": {
        "name": "Apostolic Canons (Anonymous)",
        "era": "Apostolic",
        "birth_year": None,
        "death_year": None,
        "region": "Syria",
        "bio": (
            "Eighty-five canons on church order, traditionally ascribed "
            "apostolic origin but actually compiled by an unknown hand, "
            "likely in fourth-century Syria alongside the Apostolic "
            "Constitutions. Received as canon law by the Council in "
            "Trullo (NPNF Series II, Vol. 14)."
        ),
    },
}