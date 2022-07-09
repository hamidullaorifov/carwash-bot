
from itertools import count
from re import M
import sys
sys.dont_write_bytecode = True

# Django specific settings
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()
from dotenv import load_dotenv

load_dotenv()

from db.models import *

from django.shortcuts import get_object_or_404,get_list_or_404
import datetime
from typing import Optional

# from dateutil.relativedelta import relativedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardRemove
from telegram.ext import Updater, Dispatcher, Filters, CallbackContext, \
    MessageHandler, CommandHandler, CallbackQueryHandler,ConversationHandler
from telegram import Bot
import settings
token=os.environ.get('BOT_TOKEN')
# token='5532842708:AAGV_O38VYpf0dyFoBCS312IAlWGEM8Oh6k'
updater = Updater(token=token)
dispatcher: Dispatcher = updater.dispatcher

bot = Bot(token=token)

def menu_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton('Skidka')],
        # [KeyboardButton('Ishchi qoshish'),KeyboardButton('Ishchi o\'chiris')],
        [KeyboardButton('Servis')],
    ], resize_keyboard=True, one_time_keyboard=True)



MENU_STATE,DISCOUNT_STATE,SERVICE_STATE,CAR_NUMBER_STATE,CONFIRM_NUMBER,CHECK_PASSWORD,CHANGE_PASSWORD,NEW_PASSWORD = range(8)



def start_handler(update:Update,context:CallbackContext):
    # context.bot_data.update({
    #         'login':'admin',
    #         'password':'123'
    #     })
    if 'discount' not in context.bot_data:
        context.bot_data.update(
            {
                'discount':100,
                'count':10
            }
        )
    if 'logged_in' in context.chat_data:
        del context.chat_data['logged_in']
    bd=context.bot_data
    update.message.reply_text(f"Botdan foydalanish uchun mashina raqamini kiriting.Bizda {bd['count']} tada {bd['discount']}% chegirma",reply_markup=ReplyKeyboardRemove())
    return CONFIRM_NUMBER

def admin_handler(update:Update,context:CallbackContext):
    update.message.reply_text('Menyulardan birini tanlang',reply_markup=menu_keyboard())
    return MENU_STATE

def reenter_car_number(update: Update, context: CallbackContext):
    update.callback_query.delete_message()
    update.callback_query.message.reply_text('Mashina raqamini kiriting.Masalan:01A777AA',reply_markup=ReplyKeyboardRemove())
    return CONFIRM_NUMBER
def stop_handler(update: Update, context: CallbackContext):
    update.message.reply_text('Hayr!', reply_markup=ReplyKeyboardRemove())



def add_disc(update:Update,context=CallbackContext):
    update.message.reply_text('Skidkani kiriting.Masalan 10-marta yuvishda 50% skidka 10/50')
    return DISCOUNT_STATE
def discount_handler(update:Update,context:CallbackContext):
    try:
        ans = update.message.text
        # print('ans',ans)
        parts = ans.split('/')
        count = int(parts[0])
        discount = int(parts[1])
        if discount>100 or discount<0 or count<=0:
            update.message.reply_text('Xato! Qaytadan urining')
            return add_disc(update,context)
        context.bot_data.update({
            'count':count,
            'discount':discount
        })
        users = User.objects.all()
        user_ids=set([user.user_id for user in users])
        for id in user_ids:
            bot.send_message(chat_id=id,text=f'Bizda chegirmalar {count} tada {discount}%')
        return admin_handler(update,context)
        # print(context.bot_data)
    except:
        # print('xato')
        return add_disc(update,context)






def confirm_number(update:Update,context:CallbackContext):
    callback_data = update.callback_query.data
    if callback_data == 'yes':
        number = (context.chat_data['number'])
        Service.objects.create(number=number)
        update.callback_query.delete_message()
        count_services = Service.objects.filter(number=number).count()
        discount = context.bot_data['discount']
        count = context.bot_data['count']
        # print(count_services,discount,count)
        user_id=None
        users=None
        try:
            # user=get_object_or_404(User,number=number)
            # user_id=user.user_id
            users = get_list_or_404(User,number=number)
            # print('user_id',user_id)
        except:
            pass
        if count_services%count==0:
            if users:
                try:
                    # print('aaaa')
                    for user in users:
                        bot.send_message(chat_id=user.user_id,text=f"Bizning xizmatdan foydalanganingiz uchun rahmat.Bu safar sizga {discount}% chegirma")
                    update.callback_query.message.reply_text(f"Bu foydalanauvchiga {discount}% skidka")
                    
                except Exception as e:
                    print(e)
        reply_message="Bizning xizmatdan foydalanganingiz uchun rahmat. "
        if count_services%count==count-1:
            reply_message+=f"Keyingi safar sizga {number} raqamiga {discount}% chegirma"
        elif not count_services%count==0:
            reply_message+=f"Bizda har {count}-martada {discount}% chegirma"
        if users:    
            try:
                for user in users:
                    bot.send_message(chat_id=user.user_id,text=reply_message)
                # print('ccc',msg)
            except Exception as e:
                pass
                # print('sending...',e)
            
        
        update.callback_query.message.reply_text('Saqlandi',reply_markup=menu_keyboard())
        return MENU_STATE
    elif callback_data=='no':
        return service_retry(update,context)
    elif callback_data=='ha':
        try:
            user,created = User.objects.get_or_create(user_id=update.effective_chat.id,number=context.chat_data['car_number'])
            # print(user)
            update.callback_query.delete_message()
            update.callback_query.message.reply_text("Ro'yxatdan muvoffaqiyatli o'tdingiz",reply_markup=ReplyKeyboardRemove())
        except Exception as e:
            print(e)
    elif callback_data=='yuq':
        return reenter_car_number(update,context)

def enter_car_number(update:Update,context:CallbackContext):
    try:
        text = update.message.text.upper()
        text = text.replace(' ','')
        context.chat_data.update({
            'car_number':text,
        })
        # print('update',update)
        update.message.reply_text(text=f"Raqam {text} .To\'g\'rimi?",
                                reply_markup=
                                InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton('Ha',callback_data='ha')],
                                    [InlineKeyboardButton('Yo\'q',callback_data='yuq')]]))
        # return confirm_number(update,context)
    except Exception as e:
        print(e)

def service_retry(update:Update,context:CallbackContext):
    update.callback_query.message.delete()
    update.callback_query.message.reply_text('Mashina raqamini kiriting.Masalan 70A777AA')
    return SERVICE_STATE


def service(update:Update,context:CallbackContext):
    update.message.reply_text('Mashina raqamini kiriting.Masalan 70A777AA')
    # print('service handler')
    return SERVICE_STATE
     
def service_handler(update:Update,context:CallbackContext):
    try:
        text = update.message.text.upper()
        text = text.replace(' ','')
        context.chat_data.update({
            'number':text,
        })
        # print('update',update)
        update.message.reply_text( text=f"Raqam {text} .To\'g\'rimi?",
                                reply_markup=
                                InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton('Ha',callback_data='yes')],
                                    [InlineKeyboardButton('Yo\'q',callback_data='no')]]))
        # return confirm_number(update,context)
    except Exception as e:
        print(e)

def car_number_handler(update:Update,context:CallbackContext):
    update.message.reply_text('Mashina raqamini kiriting')
    return CONFIRM_NUMBER

def checkpassword(update:Update,context:CallbackContext):
    # update.message.reply_text('Parolni kiriting')
    password = context.bot_data['password']
    text = update.message.text
    # print(text,2)
    if password==text:
        context.chat_data.update({
            'logged_in':True
        })
        return admin_handler(update,context)
    else:
        return start_handler(update,context)
def change_password(update:Update,context:CallbackContext):
    # update.message.reply_text('Parolni kiriting')
    password = context.bot_data['password']
    text = update.message.text
    # print(text,2)
    if password==text:
        context.chat_data.update({
            'logged_in':True
        })
        update.message.reply_text('Yangi parolni kiriting')
        return NEW_PASSWORD
    else:
        return start_handler(update,context)
       
def login_handler(update:Update,context:CallbackContext):
    if 'login' in context.bot_data:
        args = context.args
        if len(args)>0:
            # print(args,1)
            login = args[0]
            if login == context.bot_data['login']:
                # print(context.chat_data)
                if not 'logged_in' in context.chat_data:
                    update.message.reply_text('Parolni kiriting')
                return CHECK_PASSWORD
                # return checkpassword(update,context)
            
        return start_handler(update,context)
    else:
        context.bot_data.update({
            'login':'admin',
            'password':'123'
        })
        return login_handler(update,context)


def new_password(update:Update,context:CallbackContext):

    text = update.message.text
    context.bot_data.update({
        'password':text
    })
    # print('sdcs',context.bot_data)
    return admin_handler(update,context)


def changepass_handler(update:Update,context:CallbackContext):
    # print('changing...')
    if not 'logged_in' in context.chat_data:
        return start_handler(update,context)
    if 'login' in context.bot_data:
        args = context.args
        if len(args)>0:
            # print(args,1)
            login = args[0]
            if login == context.bot_data['login']:
                # print(context.chat_data)
                # if not 'logged_in' in context.chat_data:
                update.message.reply_text('Parolni kiriting')
                return CHANGE_PASSWORD
                # return checkpassword(update,context)
            
        return start_handler(update,context)
    else:
        return start_handler(update,context)   

def error(update:Update,context:CallbackContext):
    print('Error occured')

dispatcher.add_handler(ConversationHandler(
    entry_points=[MessageHandler(Filters.all,start_handler),],
    states={
        MENU_STATE:[
            CommandHandler('change',changepass_handler),
            MessageHandler(Filters.regex(r'^Skidka$'),add_disc),
            MessageHandler(Filters.regex(r'^Servis$'),service),
            MessageHandler(Filters.all,admin_handler),
            # MessageHandler(Filters.regex(r'^Ishchi qoshish$')),
            # MessageHandler(Filters.regex(r'^Ishchi o\'chirish$')),
            # MessageHandler(Filters.regex(r'^Buyurtma$')),
        ],
        DISCOUNT_STATE:[
            CommandHandler('change',changepass_handler),
            CommandHandler('login',login_handler),
            CommandHandler('exit',start_handler),
            CommandHandler('start',start_handler),
            MessageHandler(Filters.text,callback=discount_handler)
        ],
        SERVICE_STATE:
        [
            CommandHandler('change',changepass_handler),
            CommandHandler('login',login_handler),
            CommandHandler('exit',start_handler),
            CommandHandler('start',start_handler),
            MessageHandler(Filters.regex(r'^Skidka$'),add_disc),
            MessageHandler(Filters.regex(r'^Servis$'),service),
            MessageHandler(Filters.text,callback=service_handler),
        ],
        CONFIRM_NUMBER:
        [
            CommandHandler('change',changepass_handler),
            CommandHandler('login',login_handler),
            CommandHandler('exit',start_handler),
            CommandHandler('start',start_handler),
            MessageHandler(Filters.text,callback=enter_car_number)
        ],
        CHECK_PASSWORD:
        [
            MessageHandler(Filters.text,callback=checkpassword)
        ],
        CHANGE_PASSWORD:
        [
            MessageHandler(Filters.text,callback=change_password)
        ],
        NEW_PASSWORD:
        [
            MessageHandler(Filters.text,callback=new_password)
        ],
        

        


    },
    fallbacks=[CommandHandler('stop', stop_handler)]
))


dispatcher.add_error_handler(callback=error)
dispatcher.add_handler(CommandHandler('change',changepass_handler))
dispatcher.add_handler(CommandHandler('login',login_handler))
dispatcher.add_handler(CallbackQueryHandler(callback=confirm_number))
# dispatcher.add_handler(MessageHandler(filters=Filters.regex()))
# dispatcher.add_handler(MessageHandler(Filters.all, main_handler))
# dispatcher.add_handler(CallbackQueryHandler(callback_query_handler))

updater.start_polling()
updater.idle()
