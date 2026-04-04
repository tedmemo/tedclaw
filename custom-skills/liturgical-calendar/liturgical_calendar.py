#!/usr/bin/env python3
"""Catholic liturgical calendar — seasons, feast days, saints of the day."""
import argparse
from datetime import datetime, date

# Major feast days (month, day) -> (name, description)
FEASTS = {
    (1, 1): ("Solemnity of Mary, Mother of God", "Mary's role as Theotokos — God-bearer"),
    (1, 6): ("Epiphany", "The Magi visit the Christ child — Christ revealed to all nations"),
    (2, 2): ("Presentation of the Lord", "Jesus presented at the Temple — Simeon's prophecy"),
    (2, 14): ("Sts. Cyril and Methodius", "Patrons of Europe, brought faith to Slavic peoples"),
    (3, 19): ("St. Joseph, Spouse of Mary", "Model father — quiet, faithful, present. Patron of workers and families"),
    (3, 25): ("Annunciation", "Gabriel announces to Mary — 'Let it be done to me according to your word'"),
    (4, 25): ("St. Mark the Evangelist", "Author of the Gospel of Mark"),
    (5, 1): ("St. Joseph the Worker", "Dignity of work, sanctifying ordinary labor"),
    (5, 31): ("Visitation of Mary", "Mary visits Elizabeth — 'My soul magnifies the Lord'"),
    (6, 24): ("Birth of St. John the Baptist", "The forerunner of Christ"),
    (6, 29): ("Sts. Peter and Paul", "Pillars of the Church"),
    (7, 3): ("St. Thomas the Apostle", "From doubt to 'My Lord and my God!'"),
    (7, 22): ("St. Mary Magdalene", "Apostle to the Apostles — transformed by Christ's love"),
    (7, 26): ("Sts. Joachim and Anne", "Grandparents of Jesus, patrons of grandparents"),
    (8, 6): ("Transfiguration", "Jesus revealed in glory on the mountain"),
    (8, 14): ("St. Maximilian Kolbe", "Martyr of charity, patron of purity and consecration to Mary"),
    (8, 15): ("Assumption of Mary", "Mary taken body and soul into heaven"),
    (8, 28): ("St. Augustine", "From lust to Doctor of the Church — 'Late have I loved You'"),
    (9, 8): ("Birth of Mary", "Nativity of the Blessed Virgin"),
    (9, 14): ("Exaltation of the Holy Cross", "The Cross as victory, not defeat"),
    (9, 29): ("Sts. Michael, Gabriel, Raphael", "The Archangels — protection, message, healing"),
    (10, 1): ("St. Therese of Lisieux", "The Little Way — small acts of great love"),
    (10, 4): ("St. Francis of Assisi", "Peace, simplicity, love of creation"),
    (10, 7): ("Our Lady of the Rosary", "Power of the Rosary — weapon against evil"),
    (10, 15): ("St. Teresa of Avila", "Doctor of Prayer — 'Let nothing disturb you'"),
    (11, 1): ("All Saints Day", "Celebrating all the saints known and unknown"),
    (11, 2): ("All Souls Day", "Praying for the faithful departed"),
    (12, 6): ("St. Nicholas", "Original 'Santa Claus' — generosity to the poor"),
    (12, 8): ("Immaculate Conception", "Mary conceived without sin — patron of the Americas"),
    (12, 25): ("Christmas — Nativity of the Lord", "God became man — Emmanuel, God with us"),
    (12, 28): ("Holy Innocents", "Children killed by Herod — patron of the unborn"),
}

# Saints for daily reference (a selection for each month)
DAILY_SAINTS = {
    (1, 28): ("St. Thomas Aquinas", "Doctor of the Church, patron of students. Prayer for purity."),
    (1, 31): ("St. John Bosco", "Patron of youth — 'It is not enough to love the young, they must know they are loved.'"),
    (2, 10): ("St. Scholastica", "Twin sister of St. Benedict — power of prayer"),
    (3, 7): ("Sts. Perpetua and Felicity", "Martyrs — courage in persecution"),
    (4, 29): ("St. Catherine of Siena", "Doctor of the Church — 'Be who God meant you to be and you will set the world on fire.'"),
    (5, 13): ("Our Lady of Fatima", "Mary's call to prayer, penance, and conversion"),
    (5, 22): ("St. Rita of Cascia", "Patron of impossible causes — hope in hopelessness"),
    (6, 13): ("St. Anthony of Padua", "Patron of lost things and lost souls"),
    (6, 22): ("St. Thomas More", "Patron of lawyers and politicians — integrity under pressure"),
    (7, 11): ("St. Benedict", "Patron of Europe — 'Ora et Labora' (Pray and Work)"),
    (7, 31): ("St. Ignatius of Loyola", "Founder of Jesuits — finding God in all things"),
    (8, 8): ("St. Dominic", "Founded the Order of Preachers — power of the Rosary"),
    (8, 11): ("St. Clare of Assisi", "Followed Francis's example — radical simplicity"),
    (9, 23): ("St. Padre Pio", "Stigmatist — 'Pray, hope, and don't worry'"),
    (10, 22): ("St. John Paul II", "The Great — Theology of the Body, 'Be not afraid!'"),
    (11, 16): ("St. Margaret of Scotland", "Queen and mother — sanctity in family life"),
    (12, 14): ("St. John of the Cross", "Dark Night of the Soul — God in darkness"),
}


def get_liturgical_season(d=None):
    """Determine the liturgical season for a given date."""
    if d is None:
        d = date.today()

    month, day = d.month, d.day

    # Approximate seasons (fixed dates, moveable feasts would need Easter calc)
    if (month == 12 and day >= 1) or (month == 1 and day <= 5):
        return ("Advent/Christmas", "purple/white",
                "Season of preparation and celebration of Christ's birth. "
                "Focus: hope, anticipation, joy. Practice: Advent wreath, Jesse Tree, giving.")
    elif month == 1 and day <= 12:
        return ("Christmas", "white",
                "Celebrating the Incarnation — God became man. "
                "Focus: joy, family, gratitude for the gift of salvation.")
    elif (month == 2 and day >= 17) or (month == 3 and day <= 31):
        # Approximate Lent (varies with Easter)
        return ("Lent", "purple",
                "40 days of preparation for Easter. "
                "Focus: prayer, fasting, almsgiving. Sacrifice something meaningful. "
                "Attend Stations of the Cross on Fridays.")
    elif month == 4 and day <= 20:
        return ("Lent/Holy Week", "purple/red",
                "The most sacred week. Palm Sunday, Holy Thursday, Good Friday, Easter Vigil. "
                "Walk with Christ through His Passion.")
    elif (month == 4 and day >= 21) or (month == 5 and day <= 31):
        return ("Easter", "white/gold",
                "50 days of celebration! Christ is risen! "
                "Focus: joy, renewal, new life. The greatest feast of the Church.")
    else:
        return ("Ordinary Time", "green",
                "Growing in faith through daily life. "
                "Focus: deepening relationship with God in the ordinary. "
                "Sanctify your daily work, relationships, and struggles.")


def show_today():
    d = date.today()
    month, day = d.month, d.day
    season, color, guidance = get_liturgical_season(d)

    print(f"Liturgical Calendar — {d.strftime('%A, %B %d, %Y')}")
    print(f"  Season: {season}")
    print(f"  Color: {color}")
    print(f"  {guidance}")

    # Check feast day
    key = (month, day)
    if key in FEASTS:
        name, desc = FEASTS[key]
        print(f"\n  FEAST DAY: {name}")
        print(f"  {desc}")

    # Check saint
    if key in DAILY_SAINTS:
        name, desc = DAILY_SAINTS[key]
        print(f"\n  Saint of the Day: {name}")
        print(f"  {desc}")
    elif key in FEASTS:
        pass  # Already shown
    else:
        print(f"\n  No specific feast today — a good day for ordinary holiness.")


def show_season():
    season, color, guidance = get_liturgical_season()
    print(f"Current Liturgical Season: {season}")
    print(f"Liturgical Color: {color}")
    print(f"\n{guidance}")


def show_saint(date_str=""):
    if date_str:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        d = date.today()

    key = (d.month, d.day)
    if key in DAILY_SAINTS:
        name, desc = DAILY_SAINTS[key]
        print(f"Saint of the Day ({d.strftime('%B %d')}):")
        print(f"  {name}")
        print(f"  {desc}")
    elif key in FEASTS:
        name, desc = FEASTS[key]
        print(f"Feast Day ({d.strftime('%B %d')}):")
        print(f"  {name}")
        print(f"  {desc}")
    else:
        print(f"No specific saint listed for {d.strftime('%B %d')}.")
        print("Ask TedAngel for a saint recommendation based on your current struggles.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["today", "season", "saint"])
    parser.add_argument("--date", default="")
    args = parser.parse_args()

    if args.action == "today":
        show_today()
    elif args.action == "season":
        show_season()
    elif args.action == "saint":
        show_saint(args.date)


if __name__ == "__main__":
    main()
