# from falcon import HTTPUnauthorized, HTTPForbidden
# from src.models.user import User
#
#
# def auth_required(admin_required: bool = False):
#     def decorator(func):
#         def wrapper(self, req, *args, **kwargs):
#             current_user = req.context.get('current_user')
#             if current_user is None:
#                 raise HTTPUnauthorized
#
#             if admin_required and current_user.is_admin is False:
#                 raise HTTPForbidden
#
#             return func(self, req, *args, **kwargs)
#
#         return wrapper
#
#     return decorator
#
#
# def async_auth_required(admin_required: bool = False):
#     def decorator(func):
#         async def wrapper(self, req, *args, **kwargs):
#             current_user = req.context.get('current_user')
#             if current_user is None:
#                 raise HTTPUnauthorized
#
#             if admin_required and current_user.is_admin is False:
#                 raise HTTPForbidden
#
#             return await func(self, req, *args, **kwargs)
#
#         return wrapper
#
#     return decorator
