"""Facebook login tests.

To run::

    FACEBOOK_USER="x@example.com" FACEBOOK_PASSWORD="y" py.test websauna -s --splinter-webdriver=firefox --splinter-make-screenshot-on-failure=false --ini=test.ini -k test_facebook


"""

import os

import transaction
import pytest
from websauna.system.devop.cmdline import init_websauna

from websauna.tests.webserver import customized_web_server
from websauna.system.user.models import User


HERE = os.path.dirname(__file__)


@pytest.fixture(scope="module")
def facebook_app(request):
    """Construct a WSGI app with tutorial models and admins loaded."""
    ini_file = os.path.join(HERE, "facebook-test.ini")
    request = init_websauna(ini_file)
    return request.app


@pytest.fixture(scope="module")
def web_server(request, facebook_app):
    """Run a web server with Facebook login settings."""

    # customized_port must match one in Facebook app settings
    web_server = customized_web_server(request, facebook_app, customized_port=6662)
    return web_server()


def do_facebook_login(browser):
    """Splinter yourself in to the Facebook app."""
    b = browser

    fb_user = os.environ.get("FACEBOOK_USER")
    assert fb_user, "Please configure your Facebook secrets as environment variables to run the tests"
    fb_password = os.environ["FACEBOOK_PASSWORD"]

    assert b.is_text_present("Facebook Login")

    # FB login
    b.fill("email", fb_user)
    b.fill("pass", fb_password)
    b.find_by_css("input[name='login']").click()

    # FB allow app confirmation dialog - this is only once per user unless you reset in in your FB profile
    if b.is_text_present("will receive the following info"):
        b.find_by_css("button[name='__CONFIRM__']").click()


def do_facebook_login_if_facebook_didnt_log_us_already(browser):
    """Facebook doesn't give us login dialog again as the time is so short, or Authomatic does some caching here?."""

    if browser.is_text_present("Facebook Login"):
        do_facebook_login(browser)
    else:
        # Clicking btn-facebook-login goes directly through to the our login view
        pass


@pytest.mark.skipif("FACEBOOK_USER" not in os.environ, reason="Give Facebook user/pass as environment variables")
def test_facebook_first_login(web_server, browser, dbsession):
    """Login an user."""

    b = browser
    b.visit(web_server)

    b.click_link_by_text("Sign in")

    assert b.is_element_visible_by_css("#login-form")

    b.find_by_css(".btn-login-facebook").click()

    do_facebook_login_if_facebook_didnt_log_us_already(browser)

    assert b.is_element_present_by_css("#msg-you-are-logged-in")

    # See that we got somewhat sane data
    with transaction.manager:
        assert dbsession.query(User).count() == 1
        u = dbsession.query(User).get(1)
        assert u.first_login
        assert u.email == os.environ["FACEBOOK_USER"]
        assert u.is_admin()  # First user becomes admin
        assert u.activated_at

    b.find_by_css("#nav-logout").click()


@pytest.mark.skipif("FACEBOOK_USER" not in os.environ, reason="Give Facebook user/pass as environment variables")
def test_facebook_second_login(web_server, browser, dbsession):
    """Login second time through Facebook and see our first_login flag is unset.
    """
    b = browser

    # Initiate Facebook login with Authomatic
    b.visit("{}/login".format(web_server))
    b.find_by_css(".btn-login-facebook").click()

    do_facebook_login_if_facebook_didnt_log_us_already(b)
    assert b.is_text_present("You are now logged in")
    b.find_by_css("#nav-logout").click()

    assert b.is_element_present_by_css("#msg-logged-out")

    # And again!

    b.visit("{}/login".format(web_server))
    b.find_by_css(".btn-login-facebook").click()

    do_facebook_login_if_facebook_didnt_log_us_already(b)

    assert b.is_element_present_by_css("#msg-you-are-logged-in")

    # See that we got somewhat sane data
    with transaction.manager:
        assert dbsession.query(User).count() == 1
        u = dbsession.query(User).get(1)
        assert not u.first_login
        assert u.activated_at

    b.find_by_css("#nav-logout").click()
