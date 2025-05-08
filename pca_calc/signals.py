from django.contrib.auth.signals import user_logged_in

def unset_invitation_info(sender, user, request, **kwargs):
    """ This function clears invitation/sign up process
        after the user logins in for the first time
    """
    if 'invitation_key' in request.session.keys():
        del request.session['invitation_key']
    if 'account_verified_email' in request.session.keys():
        del request.session['account_verified_email']

user_logged_in.connect(unset_invitation_info)
