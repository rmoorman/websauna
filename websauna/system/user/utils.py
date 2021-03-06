from authomatic import Authomatic

from websauna.system.user.interfaces import IGroupClass, IUserClass, IAuthomatic, ISocialLoginMapper, ISiteCreator


def get_user_class(registry) -> IUserClass:
    user_class = registry.queryUtility(IUserClass)
    return user_class


def get_group_class(registry) -> IGroupClass:
    group_class = registry.queryUtility(IGroupClass)
    return group_class


def get_site_creator(registry) -> ISiteCreator:
    site_creator = registry.queryUtility(ISiteCreator)
    return site_creator


def get_authomatic(registry) -> Authomatic:
    """Get active Authomatic instance from the registry.

    This is registed in ``Initializer.configure_authomatic()``.
    :param registry:
    :return:
    """
    instance = registry.queryUtility(IAuthomatic)
    return instance


def get_social_login_mapper(registry, provider_id:str) -> ISocialLoginMapper:
    """Get a named social login mapper.

    Example::

        get_social_login_mapper(registry, "facebook")

    """
    return registry.queryUtility(ISocialLoginMapper, name=provider_id)