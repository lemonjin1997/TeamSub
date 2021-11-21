from ..app import app
from .sec_token import web_Token
from .sec_util import Util
from flask_mailing import Mail, Message
from flask import jsonify
from .forum_action import CheckUserModelEmail

DOMAIN_RESET_URL="https://justaforum.sitict.net/reset/token/"
DOMAIN_VERIFY_URL="https://justaforum.sitict.net/verify/token/"

# Checks email format & Sends email if email exists 
async def reset_mail(email) -> bool:
    mail = Mail()
    mail.init_app(app)
    
    if CheckUserModelEmail(email).perform():

        token = web_Token(email, None, app.config['RESET_PW_KEY'], app.config['RESET_PW_SALT']).generate_confirmation_token()
        try:        
            message = Message(
                subject="justaforum reset password link",
                recipients=[email],
                body= f"Reset token only lasts for 5min.\n{DOMAIN_RESET_URL}{token}"
                )
            await mail.send_message(message)
        
            return True
            
        except:
            return False
    
    return False

async def verify_mail(email) -> bool:
    mail = Mail()
    mail.init_app(app)

    if CheckUserModelEmail(email).perform():

        token = web_Token(email, None, app.config['RESET_PW_KEY'], app.config['RESET_PW_SALT']).generate_confirmation_token()
        
        try:
            message = Message(
                subject="justaforum verify email link",
                recipients=[email],
                body= f"Verification token only lasts for 5min.\n{DOMAIN_VERIFY_URL}{token}"
                )
            await mail.send_message(message)
            
            return True
        
        except:
            return False

    return False

# Checks token format & validate if token is tampered or expired
def validate_token(token) -> "str or False":
    # valid_result = Util(token).check_token() # add the bound

    # if valid_result:
    token_result = web_Token(None, token, app.config['RESET_PW_KEY'], app.config['RESET_PW_SALT']).confirm_token()
    if token_result:
        return token_result
    
    return False