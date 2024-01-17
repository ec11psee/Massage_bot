# Подключение библиотек
import asyncio
from aiogram import F
from aiogram.filters import Command, StateFilter
import pickle
import datetime
from datetime import timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


#Переменные для первого запуска
# global_date={}
# ids={}
#Список дней, для дальнейшего расчета
week   = [    'Monday',
              'Tuesday',
              'Wednesday',
              'Thursday',
              'Friday',
              'Saturday',
              'Sunday']

#Токен телеграм бота
TOKEN = 'token'
#Инициируем объект бота
bot = Bot(TOKEN)
dp = Dispatcher()

#Класс для определения состояния, когда нужно вписать Фамилию
class Form(StatesGroup):
    name = State()
#Класс для удобства работы с кнопками
class CallbackFactory(CallbackData, prefix='my_callback'):
    action: str
    value: str = None

#Обработка нажатия кнопки меню (Главное меню)
@dp.callback_query(CallbackFactory.filter(F.action == "main"))
async def callbacks_num_change_fab(callback: types.CallbackQuery,callback_data: CallbackFactory):
    slov={'Записаться': ['menu','zapis'],'Отменить запись': ['menu','cancel'],'Проверить записи': ['menu','check']}
    key_answer= await KeyCreater(slov)
    await callback.message.edit_text('Выберите действие', reply_markup=key_answer.as_markup())
    await callback.answer()

#Обработка выбора времени при отмене записи
@dp.callback_query(CallbackFactory.filter(F.action == "cancel"))
async def callbacks_num_change_fab(callback: types.CallbackQuery,callback_data: CallbackFactory):
    global global_date
    date_zapis=callback_data.value.replace('_',':')
    date=date_zapis.split('-')[0]
    time=date_zapis.split('-')[1]
    global_date[date][time]=None
    with open('zapis.pickle','wb') as zapis_file:
        pickle.dump(global_date,zapis_file)
    await callback.message.edit_text('Вы отменили запись!')
    await callback.answer()
    slov={'Записаться': ['menu','zapis'],'Отменить запись': ['menu','cancel'],'Проверить записи': ['menu','check']}
    key_answer= await KeyCreater(slov)
    await bot.send_message(callback.message.chat.id, 'Выберите действие', reply_markup=key_answer.as_markup())

#Обработка записи, после выбора времени
@dp.callback_query(CallbackFactory.filter(F.action == "zapis_time"))
async def callbacks_num_change_fab(callback: types.CallbackQuery,callback_data: CallbackFactory):
    global global_date
    date_zapis=callback_data.value.replace('_',':')
    date=date_zapis.split('-')[0]
    time=date_zapis.split('-')[1]
    global_date[date][time]={'id' : ids[callback.message.chat.id]}
    time=time.replace(':','_')
    slov={'ШВЗ': ['zapis_cena',f'ШВЗ-{date}-{time}'],'Спина': ['zapis_cena',f'Спина-{date}-{time}'],'Меню':["main",'none']}
    key_answer= await KeyCreater(slov)
    await callback.message.edit_text('Выберите тип массажа',reply_markup=key_answer.as_markup())
    await callback.answer()

#обработка выбора типа массажа
@dp.callback_query(CallbackFactory.filter(F.action == "zapis_cena"))
async def callbacks_num_change_fab(callback: types.CallbackQuery,callback_data: CallbackFactory):
    global global_date
    date_zapis=callback_data.value.replace('_',':')
    tip=date_zapis.split('-')[0]
    date=date_zapis.split('-')[1]
    time=date_zapis.split('-')[2]
    time=time.replace('_',':')
    global_date[date][time]['tip'] = tip
    with open('zapis.pickle','wb') as zapis_file:
        pickle.dump(global_date,zapis_file)
    await callback.message.edit_text('Вы записались!')
    await callback.answer()
    slov={'Записаться': ['menu','zapis'],'Отменить запись': ['menu','cancel'],'Проверить записи': ['menu','check']}
    key_answer= await KeyCreater(slov)
    await bot.send_message(callback.message.chat.id, 'Выберите действие', reply_markup=key_answer.as_markup())

#Обработка выбора даты
@dp.callback_query(CallbackFactory.filter(F.action == "zapis_data"))
async def callbacks_num_change_fab(callback: types.CallbackQuery,callback_data: CallbackFactory):
    global global_date
    # print(callback_data.action)
    # print(callback_data.value)
    slov={}
    for key in global_date[callback_data.value]:
        time=global_date[callback_data.value][key]
        if time == None:
            new_value=callback_data.value+'-'+key.replace(':','_')
            slov[key]=["zapis_time",new_value]
    if slov!={}:
            slov['Меню']=["main",'none']
            key_answer = await KeyCreater(slov)
            await callback.message.edit_text('Выберите время',reply_markup=key_answer.as_markup())
    else:
            await callback.message.edit_text('Все занято')
    await callback.answer()

#Обработка кнопок главного меню
@dp.callback_query(CallbackFactory.filter(F.action == "menu"))
async def callbacks_num_change_fab(callback: types.CallbackQuery,callback_data: CallbackFactory):
    # print(callback_data.action)
    # print(callback_data.value)
    if callback_data.value=='zapis':
        data1,data2 = await check_data()
        slov={str(data1): ['zapis_data',data1],str(data2): ['zapis_data',data2]}
        key_answer= await KeyCreater(slov)
        await callback.message.edit_text('Выберите дату',reply_markup=key_answer.as_markup())
    if callback_data.value=='cancel':
        slov={}
        for date in global_date.keys():
            for time in global_date[date].keys():
                if type(global_date[date][time]) is dict:
                    if global_date[date][time]['id']==ids[callback.message.chat.id]:
                        new_value=date +'-'+time.replace(':','_')
                        slov[date+' '+ time]=['cancel',new_value]
        if slov!={}:
                slov['Меню']=['main','none']
                key_answer = await KeyCreater(slov)
                await callback.message.edit_text('Выберите время',reply_markup=key_answer.as_markup())
        else:
            await callback.message.edit_text('Вы не записаны')
            slov={'Записаться': ['menu','zapis'],'Отменить запись': ['menu','cancel'],'Проверить записи': ['menu','check']}
            key_answer= await KeyCreater(slov)
            await bot.send_message(callback.message.chat.id, 'Выберите действие', reply_markup=key_answer.as_markup())
    if callback_data.value=='check':
        text=''
        for date in global_date.keys():
            for time in global_date[date].keys():
                if global_date[date][time]!=None:
                    text+= f"{date} {time} {global_date[date][time]['id']} {global_date[date][time]['tip']}\n"
        if text!='':
            await callback.message.edit_text(text)

        else:
            await callback.message.edit_text('Записей нет')
        slov={'Записаться': ['menu','zapis'],'Отменить запись': ['menu','cancel'],'Проверить записи': ['menu','check']}
        key_answer= await KeyCreater(slov)
        await bot.send_message(callback.message.chat.id, 'Выберите действие', reply_markup=key_answer.as_markup())
    #await callback.message.answer(callback_data.value)
    await callback.answer()


#Функция обновления дат для записи
async def check_data():
    global global_date
    day = datetime.datetime.today().strftime('%A')
    day_index=week.index(day)
    if day_index > 3:
         first_day = datetime.datetime.today() + timedelta(days=6-day_index)
         second_day = datetime.datetime.today() + timedelta(days=8-day_index)
    elif day_index >=1:
        first_day = datetime.datetime.today() + timedelta(days=3-day_index)
        second_day = datetime.datetime.today() + timedelta(days=8-day_index)
    else:
        first_day = datetime.datetime.today() + timedelta(days=1-day_index)
        second_day = datetime.datetime.today() + timedelta(days=3-day_index)
    first_day=first_day.strftime('%d.%m.%y')
    second_day=second_day.strftime('%d.%m.%y')
    # print(second_day)
    global_date_keys=global_date.keys()
    slovar_vremeni={
    '15:00':None,
    '15:40':None,
    '16:20':None,
    '17:00':None,
    '17:40':None
    }
    if first_day not in global_date_keys:
        for key in global_date_keys:
            del [global_date[key]]
        global_date[first_day]=dict(slovar_vremeni)
        global_date[second_day]=dict(slovar_vremeni)
    elif second_day not in global_date_keys:
        for key in global_date_keys:
            if key!=first_day:
                del [global_date[key]]
        global_date[second_day]=dict(slovar_vremeni)
    with open('zapis.pickle','wb') as zapis_file:
        pickle.dump(global_date,zapis_file)
    return [first_day,second_day]

async def KeyCreater(slovarik: list):
    keyboard = InlineKeyboardBuilder()
    for but in slovarik.keys():
        keyboard.button(text=but,callback_data=CallbackFactory(action=slovarik[but][0],value=slovarik[but][1]))
    keyboard.adjust(1)
    return keyboard


#Первоначальное действие
@dp.message(F.text,Command('start'))
async def start_message(message: types.Message,state: FSMContext):
        if message.chat.id not in ids.keys():
            await state.set_state(Form.name)
            await bot.send_message(message.chat.id, 'Введите вашу Фамилию')
        else:
            slov={'Записаться': ['menu','zapis'],'Отменить запись': ['menu','cancel'],'Проверить записи': ['menu','check']}
            key_answer= await KeyCreater(slov)
            await bot.send_message(message.chat.id, 'Выберите действие', reply_markup=key_answer.as_markup())

#Обработка Фамилии
@dp.message(F.text,Form.name)
async def reg_name(message: types.Message,state: FSMContext):
    ids[message.chat.id]=message.text
    with open('id.pickle','wb') as id_file:
        pickle.dump(ids,id_file)
    await state.clear()
    slov={'Записаться': ['menu','zapis'],'Отменить запись': ['menu','cancel'],'Проверить записи': ['menu','check']}
    key_answer= await KeyCreater(slov)
    await bot.send_message(message.chat.id, 'Выберите действие', reply_markup=key_answer.as_markup())

#Реагирование на любое сообщение
@dp.message(F.text)
async def handle_text(message: types.Message,state: FSMContext):
    if message.chat.id not in ids.keys():
        await state.set_state(Form.name)
        return await bot.send_message(message.chat.id, 'Введите вашу Фамилию')
    else:
        slov={'Записаться': ['menu','zapis'],'Отменить запись': ['menu','cancel'],'Проверить записи': ['menu','check']}
        key_answer= await KeyCreater(slov)
        await bot.send_message(message.chat.id, 'Выберите действие', reply_markup=key_answer.as_markup())

#Функция запуска бота
async def main():
    await dp.start_polling(bot)

#Старт кода
if __name__ == '__main__':
    with open('id.pickle','rb') as id_file:
        ids=pickle.load(id_file)
    with open('zapis.pickle','rb') as zapis_file:
        global_date=pickle.load(zapis_file)
    asyncio.run(main())
