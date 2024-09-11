import tg_bot_fipm.game as game


def test_get_result():
    assert game.get_points_from_answer("пушка") == 0
    assert game.get_points_from_answer("шишка") == 1
    assert game.get_points_from_answer("пенёк") == 2
    assert game.get_points_from_answer("мапинг") == 3
    assert game.get_points_from_answer("горох") == 4
    assert game.get_points_from_answer("апаль") == 5

    assert game.get_points_from_answer("ПУШКА") == 0
    assert game.get_points_from_answer("ШИШКА") == 1
    assert game.get_points_from_answer("ПЕНЁК") == 2
    assert game.get_points_from_answer("МАПИНГ") == 3
    assert game.get_points_from_answer("ГОРОХ") == 4
    assert game.get_points_from_answer("АПАЛЬ") == 5
