import logging
from datetime import datetime
import re
# from user_agents import parse
from api.models import LastSeen


import re

def gete(path):
    if re.match(r"^/product(/|$)", path):
        return 'Maxsulot Boshkaruvi'
    elif re.match(r"^/create_barcode(/|$)", path):
        return 'Barcodni rasmini yarati'
    elif re.match(r"^/product_filial(/|$)", path):
        return 'Maxsulot tahlili'
    elif re.match(r"^/filial(/|$)", path):
        return 'Filial Boshkaruvi'
    elif re.match(r"^/ombor(/|$)", path):
        return 'Ombor'
    elif re.match(r"^/omborqabul(/|$)", path):
        return 'Ombor qabul'
    elif re.match(r"^/omborqabul/\d+(/|$)", path):
        return 'Ombor qabul tarixi'
    elif re.match(r"^/omborminus(/|$)", path):
        return 'Ombordagi maxsulotlar'
    elif re.match(r"^/add_recieve_item_view(/|$)", path):
        return 'Qabulni buyumlarini qoshish'
    elif re.match(r"^/add_recieve(/|$)", path):
        return 'Qabul qoshish'
    elif re.match(r"^/delete_recieve(/|$)", path):
        return 'Qabulni ochirish'
    elif re.match(r"^/delete_recieve_item(/|$)", path):
        return 'Qabulni buyumlarini ochirish'
    elif re.match(r"^/recieve(/|$)", path):
        return 'Qabul bolimi'
    elif re.match(r"^/recieve_completion(/|$)", path):
        return 'Qabul yakunlandi'
    elif re.match(r"^/debtor(/|$)", path):
        return 'Mijozlar qarzdorligi'
    elif re.match(r"^/debtor_add(/|$)", path):
        return 'Mijoz qoshish'
    elif re.match(r"^/debtor_edit(/|$)", path):
        return 'Mijoz ozgartirildi'
    elif re.match(r"^/debtor_detail(/|$)", path):
        return 'Mijoz tarixi'
    elif re.match(r"^/deliverhistory(/|$)", path):
        return 'Yetkazib beruvchilar tarixi'
    elif re.match(r"^/product_editing_page(/|$)", path):
        return 'Maxsulot tahriri'
    elif re.match(r"^/deliver(/|$)", path):
        return 'Yetkazib beruvchilar '
    elif re.match(r"^/income_user_detail(/|$)", path):
        return 'Turli shaxslar tarixi'
    elif re.match(r"^/kassa(/|$)", path):
        return 'Kassa'
    elif re.match(r"^/filialinfo(/|$)", path):
        return 'Filial tarixi'
    elif re.match(r"^/oylik-tolash(/|$)", path):
        return 'Oylik tolash'
    elif re.match(r"^/chiqim-qilish(/|$)", path):
        return 'Chiqim qilish'
    elif re.match(r"^/chiqim_qilish_edit(/|$)", path):
        return 'Chiqim tahrirlash'
    elif re.match(r"^/kirim-qilish(/|$)", path):
        return 'Kirim qilish'
    elif re.match(r"^/kirim_qilish_edit(/|$)", path):
        return 'Kirim tahrirlash'
    elif re.match(r"^/create_deliver(/|$)", path):
        return 'Yetkazib beruvchi yaratildi'
    elif re.match(r"^/income_status_change(/|$)", path):
        return 'Filial status ozgartirildi'
    elif re.match(r"^/null_products(/|$)", path):
        return 'Maxsulot miqdori 0 ga tushurildi'
    elif re.match(r"^/all_filter(/|$)", path):
        return 'Balans hisoboti'
    elif re.match(r"^/debtor_account(/|$)", path):
        return 'Mijoz tahlili'
    elif re.match(r"^/shops(/|$)", path):
        return 'Buyurtmalar'
    elif re.match(r"^/shop_detail(/|$)", path):
        return 'Buyurtmalar tarixi'
    elif re.match(r"^/employee(/|$)", path):
        return 'Oylik ishchi'
    elif re.match(r"^/payment_employee(/|$)", path):
        return 'Oylik ishchiga tolov qilindi'
    elif re.match(r"^/flex_status_change(/|$)", path):
        return 'Oylik ishchi davamot qilish kilindi'
    elif re.match(r"^/one_day_price(/|$)", path):
        return 'Kunlik ishchi'
    elif re.match(r"^/one_day_price_add(/|$)", path):
        return 'Kunlik ishchiga tolov qilindi'
    elif re.match(r"^/one_day_status_change(/|$)", path):
        return 'Kunlik ishchini statusi ozgartirildi'
    elif re.match(r"^/user_detail_chiqim(/|$)", path):
        return 'Kunlik ishchini tarixi'
    elif re.match(r"^/detail_employee(/|$)", path):
        return 'Oylik ishchini tarixi'
    elif re.match(r"^/new_product_add(/|$)", path):
        return 'Yangi maxsulot koshildi'
    elif re.match(r"^/edit_recieve_item_view(/|$)", path):
        return 'Qabulni buyumlarini tahrirlash'
    elif re.match(r"^/call_center_payment(/|$)", path):
        return 'Call center'
    elif re.match(r"^/kassa_is_approved(/|$)", path):
        return 'Kassa tasdiklanmagan'
    elif re.match(r"^/change_chiqim_is_approved(/|$)", path):
        return 'Tasdiklanmagan chiqim tasdiklandi'
    elif re.match(r"^/change_kirim_is_approved(/|$)", path):
        return 'Tasdiklanmagan kirim tasdiklandi'
    elif re.match(r"^/detail_call_center_count(/|$)", path):
        return 'Hodim buyurtmalar tarixi'
    elif re.match(r"^/top_products(/|$)", path):
        return 'Maxsulotlar'
    elif re.match(r"^/top_delivers(/|$)", path):
        return 'Yetkazib beruvchilar'
    elif re.match(r"^/detail_top_debtors(/|$)", path):
        return 'Mijozlar buyurtma tarixi'
    elif re.match(r"^/b2c_shop(/|$)", path):
        return 'B2B savdo'
    elif re.match(r"^/b2c_shop_add(/|$)", path):
        return 'B2B savdo qoshish'
    elif re.match(r"^/b2c_shop_detail(/|$)", path):
        return 'B2B savdo tafsiloti'
    elif re.match(r"^/b2c_shop_cart_add(/|$)", path):
        return 'B2B savdo savatcha qoshildi'
    elif re.match(r"^/b2c_shop_cart_del(/|$)", path):
        return 'B2B savdo savatcha ochirildi '
    elif re.match(r"^/b2c_shop_cart_edit(/|$)", path):
        return 'B2B savdo yakunlandi '
    elif re.match(r"^/today_sales(/|$)", path):
        return 'Bugungi sotuvlar'
    elif re.match(r"^/analysis_costs(/|$)", path):
        return 'Analiz harajatlar'
    elif re.match(r"^/tovar_prixod(/|$)", path):
        return 'Kirim'
    elif re.match(r"^/tovar_prixod_tarix(/|$)", path):
        return 'Kirim tarixi'
    elif re.match(r"^/tovar_prixod_tarix_detail(/|$)", path):
        return 'Kirim tarixi tafsilotlari'
    elif re.match(r"^/money_circulation(/|$)", path):
        return 'Pul muomalasi'
    elif re.match(r"^/money_circulation_add(/|$)", path):
        return 'Pul muomalasi yaratildi'
    elif re.match(r"^/money_circulation_edit(/|$)", path):
        return 'Pul muomalasi tahrirlandi'
    elif re.match(r"^/money_circulation_delete(/|$)", path):
        return 'Pul muomalasi ochirildi'
    elif re.match(r"^/write_off(/|$)", path):
        return 'Hisobdan chiqarish'
    elif re.match(r"^/write_off_add(/|$)", path):
        return 'Hisobdan chiqarish yaratildi'
    elif re.match(r"^/write_off_item_add(/|$)", path):
        return 'Hisobdan chiqarish buyumlari yaratildi'
    elif re.match(r"^/write_off_item_delete(/|$)", path):
        return 'Hisobdan chiqarish buyumlari ochirildi'
    elif re.match(r"^/write_off_delete(/|$)", path):
        return 'Hisobdan chiqarish ochirildi'
    elif re.match(r"^/write_off_item_edit(/|$)", path):
        return 'Hisobdan chiqarish buyumlari tahrirlandi'
    elif re.match(r"^/write_off_tarix(/|$)", path):
        return 'Hisobdan chiqarish tarixi'
    elif re.match(r"^/write_off_item_detail(/|$)", path):
        return 'Hisobdan chiqarish buyumlari tafsiloti'
    elif re.match(r"^/write_off_exit(/|$)", path):
        return 'Hisobdan chiqarish yakunlandi'
    elif re.match(r"^/deliver_return(/|$)", path):
        return 'Taminotchi qaytuv'
    elif re.match(r"^/deliver_return_add(/|$)", path):
        return 'Taminotchi qaytuv yaratildi'
    elif re.match(r"^/deliver_return_item_add(/|$)", path):
        return 'Taminotchi qaytuv buyumlari yaratildi'
    elif re.match(r"^/deliver_return_tarix(/|$)", path):
        return 'Taminotchi qaytuv tarixi'
    elif re.match(r"^/deliver_return_del(/|$)", path):
        return 'Taminotchi qaytuv ochirilindi'
    elif re.match(r"^/deliver_return_item_del(/|$)", path):
        return 'Taminotchi qaytuv buyumlar ochirilindi'
    elif re.match(r"^/deliver_return_item_edit(/|$)", path):
        return 'Taminotchi qaytuv buyumlar tahrirlandi'
    elif re.match(r"^/deliver_return_item_detail(/|$)", path):
        return 'Taminotchi qaytuv buyumlar tafsiloti'
    elif re.match(r"^/deliver_return_exit(/|$)", path):
        return 'Taminotchi qaytuv yakunlandi'
    elif re.match(r"^/create_check(/|$)", path):
        return 'Savdo Check V1 yaratildi'
    elif re.match(r"^/shop_nakladnoy(/|$)", path):
        return 'Savdo Check V2 yaratildi'
    elif re.match(r"^/fin_report(/|$)", path):
        return 'Fin hisoboti'
    elif re.match(r"^/kassa_fin(/|$)", path):
        return 'Fin Kassa'
    elif re.match(r"^/exel_convert_kassa_fin(/|$)", path):
        return 'Fin Kassa exelga kochirilindi' 
    elif re.match(r"^/data_fin(/|$)", path):
        return 'Fin Malumot' 
    elif re.match(r"^/debet_kredit_fin(/|$)", path):
        return 'Fin Debet kredit'
    elif re.match(r"^/cf_fin(/|$)", path):
        return 'Fin CF'
    elif re.match(r"^/daily_cf_fin(/|$)", path):
        return 'Fin Kunlik CF'
    elif re.match(r"^/xarid_fin(/|$)", path):
        return 'Fin Xarid'
    elif re.match(r"^/sotuv_fin(/|$)", path):
        return 'Fin Sotuv'
    elif re.match(r"^/pl_fin(/|$)", path):
        return 'Fin P/L'
    elif re.match(r"^/balans_fin(/|$)", path):
        return 'Fin Balans'
    elif re.match(r"^/majburiyat_fin(/|$)", path):
        return 'Fin Majburiyat'
    elif re.match(r"^/tolov_kalendar_fin(/|$)", path):
        return 'Fin Tolov kalendari'
    elif re.match(r"^/reja_tushum_fin(/|$)", path):
        return 'Fin Reja tushum'
    elif re.match(r"^/reja_tushum_fin_add(/|$)", path):
        return 'Fin Reja tushum yaratildi'
    elif re.match(r"^/reja_tushum_fin_edit(/|$)", path):
        return 'Fin Reja tushum tahrirlandi'
    elif re.match(r"^/reja_tushum_fin_del(/|$)", path):
        return 'Fin Reja tushum ochirildi'
    
    elif re.match(r"^/reja_chiqim_fin(/|$)", path):
        return 'Fin Reja chiqim'
    elif re.match(r"^/reja_chiqim_fin_add(/|$)", path):
        return 'Fin Reja chiqim yaratildi'
    elif re.match(r"^/reja_chiqim_fin_edit(/|$)", path):
        return 'Fin Reja chiqim tahrirlandi'
    elif re.match(r"^/reja_chiqim_fin_del(/|$)", path):
        return 'Fin Reja chiqim ochirildi'
    elif re.match(r"^/asosiy_vosita_fin(/|$)", path):
        return 'Fin Asosiy vosita'
    elif re.match(r"^/add_main_tool_type(/|$)", path):
        return 'Fin Asosiy vosita turi qoshildi'
    elif re.match(r"^/add_main_tool(/|$)", path):
        return 'Fin Asosiy vosita qoshildi'
    elif re.match(r"^/edit_main_tool(/|$)", path):
        return 'Fin Asosiy vosita tahrirlandi'
    elif re.match(r"^/ombor_fin(/|$)", path):
        return 'Fin Ombor'
    
    elif re.match(r"^/b2b_shop(/|$)", path):
        return 'B2B savdo'
    elif re.match(r"^/b2b_shop_add(/|$)", path):
        return 'B2B savdo qoshildi'
    elif re.match(r"^/b2b_shop_ajax(/|$)", path):
        return 'B2B savdo tafsiloti'
    elif re.match(r"^/b2b_shop_ajax_edit(/|$)", path):
        return 'B2B savdo tahrirlandi'
    elif re.match(r"^/payment_shop_ajax(/|$)", path):
        return 'B2B savdo tafsilot pul tolandi'
    elif re.match(r"^/b2b_shop_ajax_add_one(/|$)", path):
        return 'B2B savdo tafsilot savatcha qoshildi'
    elif re.match(r"^/b2b_shop_ajax_cart_delete(/|$)", path):
        return 'B2B savdo tafsilot savatcha ochirildi'
    elif re.match(r"^/nds_page(/|$)", path):
        return 'NDS'
    elif re.match(r"^/users_restrictions(/|$)", path):
        return 'Foydalanuvchilar'
    elif re.match(r"^/users_restrictions_limit(/|$)", path):
        return 'Foydalanuvchilar tafsiloti'
    elif re.match(r"^/users_add(/|$)", path):
        return 'Foydalanuvchilar yaratildi'
    elif re.match(r"^/product_remove_quantity(/|$)", path):
        return 'B2B savdo tafsilotlar reja tushum yaratildi '
    elif re.match(r"^/users_change(/|$)", path):
        return 'Foydalanuvchi tahrirlandi'
    elif re.match(r"^/users_delete(/|$)", path):
        return 'Foydalanuvchi ochirildi'
    
    elif re.match(r"^/price_type(/|$)", path):
        return 'Narx turi'
    elif re.match(r"^/price_type_add(/|$)", path):
        return 'Narx turi yartildi'
    elif re.match(r"^/price_type_edit(/|$)", path):
        return 'Narx turi tahrirlandi'
    elif re.match(r"^/price_type_del(/|$)", path):
        return 'Narx turi ochirildi'
   
    elif re.match(r"^/add_product_price_type(/|$)", path):
        return 'Narx turi maxsulotlari qoshildi'
    
    elif re.match(r"^/product_price_type/\d+(/|$)", path):
        return 'Narx turi maxsulotlari'
    elif re.match(r"^/filial_list(/|$)", path):
        return 'Filiallar ro\'yxati'
    elif re.match(r"^/filial_add(/|$)", path):
        return 'Filial qo\'shish'
    elif re.match(r"^/filial_edit/\d+(/|$)", path):
        return 'Filial tahrirlash'
    elif re.match(r"^/filial_del/\d+(/|$)", path):
        return 'Filial o\'chirish'
    elif re.match(r"^/externalincomeuser(/|$)", path):
        return 'Tashqi foydalanuvchilar'
    elif re.match(r"^/externalincomeuser_add(/|$)", path):
        return 'Tashqi foydalanuvchi qo\'shish'
    elif re.match(r"^/externalincomeuser_edit/\d+(/|$)", path):
        return 'Tashqi foydalanuvchi tahrirlash'
    elif re.match(r"^/external_income_user_types_add(/|$)", path):
        return 'Tashqi foydalanuvchi turi qo\'shish'
    elif re.match(r"^/income_payment/\d+(/|$)", path):
        return 'Tolov qilish'
    elif re.match(r"^/income_give/\d+(/|$)", path):
        return 'Pul berish'
    elif re.match(r"^/valyuta_list(/|$)", path):
        return 'Valyutalar ro\'yxati'
    elif re.match(r"^/valyuta_add(/|$)", path):
        return 'Valyuta qo\'shish'
    elif re.match(r"^/valyuta_edit/\d+(/|$)", path):
        return 'Valyuta tahrirlash'
    elif re.match(r"^/kassa_merge(/|$)", path):
        return 'Kassalarni birlashtirish'
    elif re.match(r"^/kassa_merge_add(/|$)", path):
        return 'Kassalarni birlashtirish qo\'shish'
    elif re.match(r"^/kassa_merge_edit/\d+(/|$)", path):
        return 'Kassalarni birlashtirish tahrirlash'
    elif re.match(r"^/kassa_merge_del/\d+(/|$)", path):
        return 'Kassalarni birlashtirish o\'chirish'
    elif re.match(r"^/kassa_new_list(/|$)", path):
        return 'Yangi kassalar ro\'yxati'
    elif re.match(r"^/kassa_new_add(/|$)", path):
        return 'Yangi kassa qo\'shish'
    elif re.match(r"^/kassa_new_edit/\d+(/|$)", path):
        return 'Yangi kassa tahrirlash'
    elif re.match(r"^/add_bonus(/|$)", path):
        return 'Bonus qo\'shish'
    elif re.match(r"^/set_start_summa(/|$)", path):
        return 'Boshlang\'ich summani o\'rnatish'
    elif re.match(r"^/filial_kassalar(/|$)", path):
        return 'Filial kassalari'
    elif re.match(r"^/get_product_prices(/|$)", path):
        return 'Maxsulot narxlari'
    elif re.match(r"^/customer_debt_create/\d+(/|$)", path):
        return 'Mijoz qarzi yaratish'
    elif re.match(r"^/external_income_user_debt_create/\d+(/|$)", path):
        return 'Tashqi foydalanuvchi qarzi yaratish'
    elif re.match(r"^/externalincomeuser_detail/\d+(/|$)", path):
        return 'Tashqi foydalanuvchi tafsiloti'
    elif re.match(r"^/majburiyat_chiqim_fin_add(/|$)", path):
        return 'Majburiyat chiqim qo\'shish'
    elif re.match(r"^/recieve-expanse/add(/|$)", path):
        return 'Xarajat qo\'shish'
    elif re.match(r"^/add_expanse_type(/|$)", path):
        return 'Xarajat turi qo\'shish'
    elif re.match(r"^/recieve-expanse/\d+/edit(/|$)", path):
        return 'Xarajat tahrirlash'
    elif re.match(r"^/recieve-expanse/\d+/delete(/|$)", path):
        return 'Xarajat o\'chirish'
    elif re.match(r"^/reja_chiqim_bajarish/\d+(/|$)", path):
        return 'Reja chiqim bajarish'
    elif re.match(r"^/todays_practices(/|$)", path):
        return 'Bugungi amaliyotlar'
    elif re.match(r"^/reviziya(/|$)", path):
        return 'Reviziya'
    elif re.match(r"^/revision_add(/|$)", path):
        return 'Reviziya qo\'shish'
    elif re.match(r"^/list_product_price_revision(/|$)", path):
        return 'Maxsulot narxlari reviziyasi'
    elif re.match(r"^/revision_detail/\d+(/|$)", path):
        return 'Reviziya tafsiloti'
    elif re.match(r"^/revision_item_add/\d+(/|$)", path):
        return 'Reviziya elementi qo\'shish'
    elif re.match(r"^/revision_one_item_add/\d+(/|$)", path):
        return 'Reviziya bitta element qo\'shish'
    elif re.match(r"^/revision_one_item_del/\d+(/|$)", path):
        return 'Reviziya bitta element o\'chirish'
    elif re.match(r"^/revison_complate/\d+(/|$)", path):
        return 'Reviziya yakunlandi'
    elif re.match(r"^/revision_complate(/|$)", path):
        return 'Yakunlangan reviziyalar'
    elif re.match(r"^/revision_complate_items/\d+(/|$)", path):
        return 'Yakunlangan reviziya elementlari'
    elif re.match(r"^/measurement_type_list(/|$)", path):
        return 'O\'lchov turlari'
    elif re.match(r"^/measurement_type_add(/|$)", path):
        return 'O\'lchov turi qo\'shish'
    elif re.match(r"^/measurement_type_edit/\d+(/|$)", path):
        return 'O\'lchov turi tahrirlash'
    elif re.match(r"^/measurement_type_del/\d+(/|$)", path):
        return 'O\'lchov turi o\'chirish'
    elif re.match(r"^/for_pro(/|$)", path):
        return 'Pro uchun'
    elif re.match(r"^/mobile_order_list(/|$)", path):
        return 'Mobil buyurtmalar'
    elif re.match(r"^/mobile_order_detail/\d+(/|$)", path):
        return 'Mobil buyurtma tafsiloti'
    elif re.match(r"^/morder_change_status/\d+(/|$)", path):
        return 'Mobil buyurtma statusini o\'zgartirish'
    elif re.match(r"^/b2c_naqd_add(/|$)", path):
        return 'B2C naqd qo\'shish'
    elif re.match(r"^/upload_excel(/|$)", path):
        return 'Excel yuklash'
    elif re.match(r"^/edit_product_prices(/|$)", path):
        return 'Maxsulot narxlarini tahrirlash'
    elif re.match(r"^/create-debtor-type(/|$)", path):
        return 'Qarzdor turi yaratish'
    elif re.match(r"^/create-price-type(/|$)", path):
        return 'Narx turi yaratish'
    elif re.match(r"^/create-teritory(/|$)", path):
        return 'Hudud yaratish'
    elif re.match(r"^/create-region(/|$)", path):
        return 'Viloyat yaratish'
    elif re.match(r"^/create-deliver-new(/|$)", path):
        return 'Yetkazib beruvchi yaratish'
    elif re.match(r"^/create-measurement(/|$)", path):
        return 'O\'lchov yaratish'
    elif re.match(r"^/create-group(/|$)", path):
        return 'Guruh yaratish'
    elif re.match(r"^/b2c_shop_edit(/|$)", path):
        return 'B2C do\'kon tahrirlash'
    elif re.match(r"^/api/video-tutorial/check(/|$)", path):
        return 'Video darslikni tekshirish'
    elif re.match(r"^/api/video-tutorial/save(/|$)", path):
        return 'Video darslikni saqlash'
    elif re.match(r"^/api/video-tutorial/delete(/|$)", path):
        return 'Video darslikni o\'chirish'
    elif re.match(r"^/expiring-shop(/|$)", path):
        return 'Muddati tugaydigan buyurtmalar'
    elif re.match(r"^/last_seen(/|$)", path):
        return 'Oxirgi ko\'rilgan'
    else:
        return 'Noma\'lum yo\'l'
    

    
def devices(request):
    # user_agent_str = request.META.get('HTTP_USER_AGENT', '')
    # user_agent = parse(user_agent_str)

    # os_name = user_agent.os.family
    # browser_name = user_agent.browser.family

    # if 'Windows' in os_name or 'Mac' in os_name or 'Linux' in os_name:
    #     device_type = 'Kompyuter'
    #     device_name = os_name 
    # elif user_agent.is_mobile:
    #     device_type = 'Telefon'
    #     device_name = user_agent.device.family
    # elif user_agent.is_tablet:
    #     device_type = 'Planshet'
    #     device_name = user_agent.device.family
    # elif user_agent.is_bot:
    #     device_type = 'Bot'
    #     device_name = "Bot"
    # else:
    #     device_type = 'Noma’lum'
    #     device_name = "Noma’lum qurilma"

    return f"{1} | {1} | {1}"

logger = logging.getLogger(__name__)

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        method = request.method
        user = request.user if request.user.is_authenticated else "Anonim"
        ip = request.META.get('REMOTE_ADDR')
        agent = request.META.get('HTTP_USER_AGENT', '')
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        
        if path not in '/api/video-tutorial/check/':
            device = devices(request)
            what_did = gete(path)
            if user and what_did != 'Noma\'lum yo\'l':
                LastSeen.objects.create(device=device, what_did=what_did, user=user)
            print(f"[{time}] 👤 {user} | {method} {path} | IP: {ip} | Agent: {agent}")

        return self.get_response(request)
