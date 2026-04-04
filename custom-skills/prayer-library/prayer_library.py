#!/usr/bin/env python3
"""Catholic prayer library, Bible verses, saints quotes, and confession prep."""
import argparse
import random

PRAYERS = {
    "strength": {
        "title": "Prayer for Strength",
        "text": "Lord God, give me the strength to resist temptation today. When I am weak, You are strong. Fill me with Your Holy Spirit so that I may walk in freedom and dignity. I place my trust in You, not in my own willpower. Through Christ our Lord. Amen."
    },
    "purity": {
        "title": "Prayer for Purity (St. Thomas Aquinas)",
        "text": "Dear Lord, grant me the grace of purity in thought, word, and deed. Cleanse my heart of all impure desires and fill me with the strength to resist temptation. Help me to see myself and others as temples of the Holy Spirit, worthy of respect and love. Through the intercession of the Blessed Virgin Mary, most pure, guard my eyes, my mind, and my body. Amen."
    },
    "protection": {
        "title": "Prayer to St. Michael the Archangel",
        "text": "St. Michael the Archangel, defend us in battle. Be our protection against the wickedness and snares of the devil. May God rebuke him, we humbly pray, and do thou, O Prince of the heavenly hosts, by the power of God, cast into hell Satan, and all the evil spirits, who prowl about the world seeking the ruin of souls. Amen."
    },
    "marriage": {
        "title": "Prayer for Marriage",
        "text": "Lord, bless our marriage. Help us to love each other as You love the Church — with patience, sacrifice, and faithfulness. Heal the wounds between us. Give us the grace to forgive, to listen, and to choose each other again today. Protect our family. Unite us in Your love. Through Christ our Lord. Amen."
    },
    "anxiety": {
        "title": "Prayer for Peace and Anxiety",
        "text": "Lord, I give You my anxious thoughts. You said 'Do not be anxious about anything, but in every situation, by prayer and petition, with thanksgiving, present your requests to God. And the peace of God, which transcends all understanding, will guard your hearts and your minds in Christ Jesus.' I claim that peace now. Help me trust Your plan. Amen."
    },
    "morning": {
        "title": "Morning Offering",
        "text": "O Jesus, through the Immaculate Heart of Mary, I offer You my prayers, works, joys, and sufferings of this day, in union with the Holy Sacrifice of the Mass throughout the world. I offer them for all the intentions of Your Sacred Heart: the salvation of souls, reparation for sin, and the reunion of all Christians. I offer them for the intentions of our bishops and of all Apostles of Prayer, and in particular for those recommended by our Holy Father this month. Amen."
    },
    "evening": {
        "title": "Evening Examen (St. Ignatius)",
        "text": "1. GRATITUDE: Lord, thank You for the gifts of this day.\n2. PRESENCE: Help me see where You were present today.\n3. EMOTIONS: What feelings did I experience? What do they tell me?\n4. CHALLENGE: Where did I fall short? Where did I struggle?\n5. TOMORROW: Lord, give me grace for tomorrow. Help me grow.\n\nOur Father, who art in heaven, hallowed be Thy name. Thy kingdom come, Thy will be done, on earth as it is in heaven. Give us this day our daily bread, and forgive us our trespasses, as we forgive those who trespass against us. And lead us not into temptation, but deliver us from evil. Amen."
    },
    "contrition": {
        "title": "Act of Contrition",
        "text": "O my God, I am heartily sorry for having offended Thee, and I detest all my sins because of Thy just punishments, but most of all because they offend Thee, my God, who art all-good and deserving of all my love. I firmly resolve, with the help of Thy grace, to sin no more and to avoid the near occasions of sin. Amen."
    },
    "temptation": {
        "title": "Prayer During Temptation",
        "text": "Jesus, I trust in You. St. Michael, defend me. Blessed Mother, cover me with your mantle. I am a child of God. This urge will pass. I choose freedom. I choose dignity. Lord, give me strength for the next 15 minutes. I can do all things through Christ who strengthens me. Amen."
    },
    "peace": {
        "title": "Prayer of St. Francis",
        "text": "Lord, make me an instrument of Your peace. Where there is hatred, let me sow love; where there is injury, pardon; where there is doubt, faith; where there is despair, hope; where there is darkness, light; where there is sadness, joy. O Divine Master, grant that I may not so much seek to be consoled as to console, to be understood as to understand, to be loved as to love. For it is in giving that we receive, in pardoning that we are pardoned, and in dying that we are born to eternal life. Amen."
    },
    "forgiveness": {
        "title": "Prayer for Forgiveness",
        "text": "Lord, I have sinned against You and against others. I am truly sorry. Help me to forgive myself as You forgive me. Help me to forgive those who have hurt me. Free me from bitterness and resentment. Give me a clean heart. Wash me, and I shall be whiter than snow. Through the Blood of Christ. Amen."
    },
    "family": {
        "title": "Prayer for Family",
        "text": "Heavenly Father, bless and protect my family. Give me patience with my children and wisdom to guide them. Help me be present, not distracted. Heal any brokenness between us. St. Joseph, model of fathers, pray for me. Holy Family of Nazareth, make our family holy. Amen."
    },
    "work": {
        "title": "Prayer Before Work",
        "text": "Lord, I offer this day's work to You. Whatever I do, help me do it with all my heart, as working for You and not for human masters. Give me patience with difficult people, focus on my tasks, and peace in stress. Sanctify my ordinary work. Through Christ our Lord. Amen."
    },
    "suffering": {
        "title": "Prayer in Suffering",
        "text": "Lord, I am in pain. I don't understand why this is happening. But I trust that You are with me. Help me unite my suffering to Yours on the Cross. 'My grace is sufficient for you, for my power is made perfect in weakness.' Give me the grace to endure. I offer this suffering for the souls in purgatory and for my own purification. Amen."
    },
    "rosary": {
        "title": "How to Pray the Rosary (Quick Guide)",
        "text": "1. Sign of the Cross + Apostles' Creed\n2. Our Father\n3. Three Hail Marys (faith, hope, charity)\n4. Glory Be\n5. Announce the Mystery, then:\n   - Our Father\n   - 10 Hail Marys (one decade)\n   - Glory Be\n   - O My Jesus (Fatima Prayer)\n6. Repeat for 5 decades\n7. Hail Holy Queen\n8. Sign of the Cross\n\nToday's Mysteries:\n- Monday/Saturday: Joyful\n- Tuesday/Friday: Sorrowful\n- Wednesday/Sunday: Glorious\n- Thursday: Luminous"
    },
}

VERSES = {
    "temptation": [
        ("1 Corinthians 10:13", "No temptation has overtaken you except what is common to mankind. And God is faithful; he will not let you be tempted beyond what you can bear. But when you are tempted, he will also provide a way out so that you can endure it."),
        ("James 4:7", "Submit yourselves, then, to God. Resist the devil, and he will flee from you."),
        ("Galatians 5:16", "So I say, walk by the Spirit, and you will not gratify the desires of the flesh."),
    ],
    "hope": [
        ("Jeremiah 29:11", "For I know the plans I have for you, declares the LORD, plans to prosper you and not to harm you, plans to give you hope and a future."),
        ("Romans 8:28", "And we know that in all things God works for the good of those who love him, who have been called according to his purpose."),
        ("Isaiah 40:31", "But those who hope in the LORD will renew their strength. They will soar on wings like eagles; they will run and not grow weary, they will walk and not be faint."),
    ],
    "anger": [
        ("Ephesians 4:26-27", "In your anger do not sin. Do not let the sun go down while you are still angry, and do not give the devil a foothold."),
        ("James 1:19-20", "Everyone should be quick to listen, slow to speak and slow to become angry, because human anger does not produce the righteousness that God desires."),
        ("Proverbs 14:29", "Whoever is patient has great understanding, but one who is quick-tempered displays folly."),
    ],
    "strength": [
        ("Philippians 4:13", "I can do all things through Christ who strengthens me."),
        ("2 Timothy 1:7", "For God has not given us a spirit of fear, but of power and of love and of a sound mind."),
        ("Isaiah 41:10", "So do not fear, for I am with you; do not be dismayed, for I am your God. I will strengthen you and help you; I will uphold you with my righteous right hand."),
    ],
    "peace": [
        ("Philippians 4:6-7", "Do not be anxious about anything, but in every situation, by prayer and petition, with thanksgiving, present your requests to God. And the peace of God, which transcends all understanding, will guard your hearts and your minds in Christ Jesus."),
        ("John 14:27", "Peace I leave with you; my peace I give you. I do not give to you as the world gives. Do not let your hearts be troubled and do not be afraid."),
    ],
    "marriage": [
        ("Ephesians 5:25", "Husbands, love your wives, just as Christ loved the church and gave himself up for her."),
        ("1 Corinthians 13:4-7", "Love is patient, love is kind. It does not envy, it does not boast, it is not proud. It does not dishonor others, it is not self-seeking, it is not easily angered, it keeps no record of wrongs. Love does not delight in evil but rejoices with the truth. It always protects, always trusts, always hopes, always perseveres."),
    ],
    "suffering": [
        ("2 Corinthians 12:9", "My grace is sufficient for you, for my power is made perfect in weakness."),
        ("Romans 8:18", "I consider that our present sufferings are not worth comparing with the glory that will be revealed in us."),
        ("Psalm 34:18", "The LORD is close to the brokenhearted and saves those who are crushed in spirit."),
    ],
    "forgiveness": [
        ("1 John 1:9", "If we confess our sins, he is faithful and just and will forgive us our sins and purify us from all unrighteousness."),
        ("Romans 8:1", "Therefore, there is now no condemnation for those who are in Christ Jesus."),
        ("Psalm 103:12", "As far as the east is from the west, so far has he removed our transgressions from us."),
    ],
    "love": [
        ("1 John 4:18", "There is no fear in love. But perfect love drives out fear."),
        ("Romans 8:38-39", "For I am convinced that neither death nor life, neither angels nor demons, neither the present nor the future, nor any powers, neither height nor depth, nor anything else in all creation, will be able to separate us from the love of God that is in Christ Jesus our Lord."),
    ],
    "fear": [
        ("Psalm 23:4", "Even though I walk through the darkest valley, I will fear no evil, for you are with me; your rod and your staff, they comfort me."),
        ("Deuteronomy 31:6", "Be strong and courageous. Do not be afraid or terrified because of them, for the LORD your God goes with you; he will never leave you nor forsake you."),
    ],
    "patience": [
        ("Romans 12:12", "Be joyful in hope, patient in affliction, faithful in prayer."),
        ("Galatians 6:9", "Let us not become weary in doing good, for at the proper time we will reap a harvest if we do not give up."),
    ],
    "gratitude": [
        ("1 Thessalonians 5:18", "Give thanks in all circumstances; for this is God's will for you in Christ Jesus."),
        ("Psalm 118:24", "This is the day the LORD has made; let us rejoice and be glad in it."),
    ],
}

SAINTS = [
    ("St. Augustine", "Late have I loved You, O Beauty so ancient and so new, late have I loved You! You were within me, but I was outside."),
    ("St. Augustine", "Our hearts are restless until they rest in You, O Lord."),
    ("St. Josemaria Escriva", "A saint is a sinner who keeps trying."),
    ("St. Francis de Sales", "Be patient with everyone, but above all with yourself. Do not be disheartened by your imperfections."),
    ("St. Padre Pio", "Pray, hope, and don't worry. Worry is useless. God is merciful and will hear your prayer."),
    ("St. Teresa of Calcutta", "If you judge people, you have no time to love them."),
    ("St. Therese of Lisieux", "Miss no single opportunity of making some small sacrifice, here by a smiling look, there by a kindly word."),
    ("St. John Paul II", "Do not be afraid. Do not be satisfied with mediocrity. Put out into the deep and let down your nets for a catch."),
    ("St. Thomas More", "Lord, give me the grace to change the things I can, to accept the things I cannot, and the wisdom to know the difference."),
    ("St. Monica", "Nothing is far from God. (She prayed 17 years for her son Augustine's conversion — and it happened.)"),
    ("St. Maximilian Kolbe", "The most deadly poison of our times is indifference. Let us not be indifferent."),
    ("St. Ignatius of Loyola", "Take, Lord, and receive all my liberty, my memory, my understanding, and my entire will."),
    ("Bl. Carlo Acutis", "The Eucharist is my highway to heaven. (A modern saint who died at 15, showing faith and technology can coexist.)"),
]

CONFESSION = """Examination of Conscience — Preparation for Confession

Take a moment of silence. Ask the Holy Spirit to help you see clearly.

THE 10 COMMANDMENTS:

1. I am the Lord your God — Have I put anything before God? (Work, phone, habits?)
2. Do not take God's name in vain — Have I used God's name carelessly?
3. Keep holy the Lord's Day — Have I missed Mass without good reason?
4. Honor your father and mother — Have I been disrespectful to my parents or in-laws?
5. You shall not kill — Have I harbored anger, hatred, or unforgiveness?
6. You shall not commit adultery — Have I been unfaithful in thought or action? Pornography? Masturbation?
7. You shall not steal — Have I taken what isn't mine? Been dishonest at work?
8. You shall not bear false witness — Have I lied? Gossiped? Damaged someone's reputation?
9. You shall not covet your neighbor's wife — Have I lusted after someone?
10. You shall not covet your neighbor's goods — Have I been envious or greedy?

ADDITIONAL REFLECTION:
- Have I been patient with my children?
- Have I been a loving husband/partner?
- Have I been honest with myself about my struggles?
- Have I avoided Confession out of shame?

REMEMBER:
- God already knows your sins. Confession is for YOUR healing.
- The priest has heard it all. There is nothing you can say that will shock him.
- "If we confess our sins, he is faithful and just and will forgive us." (1 John 1:9)

After examining your conscience, go to Confession and say:
"Bless me, Father, for I have sinned. It has been [time] since my last confession. These are my sins: [confess sins]. For these and all my sins, I am truly sorry."

Then pray the Act of Contrition when the priest asks."""


def get_prayer(topic):
    topic = topic.lower().strip()
    if topic in PRAYERS:
        p = PRAYERS[topic]
        print(f"{p['title']}\n")
        print(p["text"])
    else:
        available = ", ".join(sorted(PRAYERS.keys()))
        print(f"Prayer topic '{topic}' not found. Available: {available}")


def get_verse(topic):
    topic = topic.lower().strip()
    if topic in VERSES:
        verse = random.choice(VERSES[topic])
        print(f"{verse[0]}\n\n\"{verse[1]}\"")
    else:
        available = ", ".join(sorted(VERSES.keys()))
        print(f"Verse topic '{topic}' not found. Available: {available}")


def get_saint():
    saint, quote = random.choice(SAINTS)
    print(f"{saint}:\n\n\"{quote}\"")


def show_confession():
    print(CONFESSION)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prayer", "verse", "saint", "confession"])
    parser.add_argument("--topic", default="strength")
    args = parser.parse_args()

    if args.action == "prayer":
        get_prayer(args.topic)
    elif args.action == "verse":
        get_verse(args.topic)
    elif args.action == "saint":
        get_saint()
    elif args.action == "confession":
        show_confession()


if __name__ == "__main__":
    main()
