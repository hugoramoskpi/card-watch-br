from src.bot.bot import format_status_message, format_promo_list

def test_format_status_message():
    msg = format_status_message(cards_found=5, promos_validated=2, alerts_sent=1)
    assert "5" in msg
    assert "2" in msg
    assert "1" in msg

def test_format_promo_list_empty():
    msg = format_promo_list([])
    assert "nenhuma" in msg.lower()

def test_format_promo_list_with_promos():
    promos = [{"card_name": "Inter Black", "summary": "Anuidade zero", "confidence": 2}]
    msg = format_promo_list(promos)
    assert "Inter Black" in msg
    assert "Anuidade zero" in msg
