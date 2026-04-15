import os
import random
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

# ─── ВСЕ ВОПРОСЫ ──────────────────────────────────────────────────────────────
QUESTIONS = [
    # IV LYGIS — 1 ETAPAS
    {"q":"Kokius teisės aktus leidžia Respublikos Prezidentas?","opts":["Įsakymus","Nutarimus","Įsakus","Dekretus"],"answer":3,"explain":"Konstitucijos 85 str.: Respublikos Prezidentas leidžia dekretus."},
    {"q":"Konstitucijoje įvardijami ypatinga tvarka priimami ir keičiami įstatymai vadinasi:","opts":["Kodeksai","Programiniai įstatymai","Organiniai įstatymai","Konstituciniai įstatymai"],"answer":3,"explain":"Konstitucijos 69 str. 3 d.: konstituciniai įstatymai priimami daugiau kaip pusės visų Seimo narių balsų dauguma."},
    {"q":"Kas skiria ir atleidžia Aukščiausiojo Teismo teisėjus?","opts":["Respublikos Prezidentas Seimo pritarimu","Seimas Respublikos Prezidento teikimu","Respublikos Prezidentas Teisėjų tarybos siūlymu","Respublikos Prezidentas"],"answer":1,"explain":"Konstitucijos 112 str. 3 d.: Aukščiausiojo Teismo teisėjus skiria ir atleidžia Seimas Respublikos Prezidento teikimu."},
    {"q":"Kurie iš Konstitucijoje nurodytų specializuotų teismų veikia Lietuvoje?","opts":["Administraciniai teismai","Darbo bylas nagrinėjantys teismai","Visų nurodytų rūšių specializuoti teismai","Šeimos bylas nagrinėjantys teismai"],"answer":0,"explain":"Konstitucijos 111 str. 2 d.: Lietuvoje veikia administraciniai specializuoti teismai. Darbo ir šeimos teismų nėra."},
    {"q":"Kokios pasekmės, jei Seimo narys neprisiekia arba prisiekia lygtinai?","opts":["Seimo narys netenka Seimo nario mandato","Seimas kreipasi į Konstitucinį Teismą","Seimo narys skiriamas į kitą tarnybą","Seimo narys laikinai suspenduojamas"],"answer":0,"explain":"Konstitucijos 59 str. 3 d.: Seimo narys, įstatymo nustatyta tvarka neprisiekęs arba prisiekęs lygtinai, netenka Seimo nario mandato."},
    {"q":"Kaip turi elgtis teisėjas, kai mano, kad taikytinas teisės aktas prieštarauja Konstitucijai?","opts":["Gali pats nuspręsti netaikyti tokio akto","Sustabdo bylą ir kreipiasi į Konstitucinį Teismą","Kreipiasi į Aukščiausiąjį Teismą","Nagrinėja bylą toliau, rašo atskirąją nuomonę"],"answer":1,"explain":"Konstitucijos 110 str. 2 d.: teisėjas sustabdo bylos nagrinėjimą ir kreipiasi į Konstitucinį Teismą."},
    {"q":"Kas vykdo Seimo kontrolierių įstaigos funkcijas?","opts":["Seimo skiriami pareigūnai, tiriantys skundus dėl valdžios savivalės","Seimas per komitetą","Prezidento skiriami ombudsmenai","Vyriausybės inspektoriai"],"answer":0,"explain":"Konstitucijos 73 str.: Seimo kontrolieriai tiria piliečių skundus dėl valdžios įstaigų pareigūnų piktnaudžiavimo ir biurokratizmo."},
    {"q":"Kas yra aukščiausioji valstybinė audito institucija?","opts":["Finansų ministerija","Valstybės kontrolė","Seimo Audito komitetas","Lietuvos bankas"],"answer":1,"explain":"Konstitucijos 133 str. 1 d.: Valstybės kontrolė yra aukščiausioji valstybinė audito institucija."},
    {"q":"Kiek laiko Respublikos Prezidentas gali eiti pareigas iš eilės?","opts":["Ne daugiau kaip dvi kadencijas iš eilės","Ne daugiau kaip vieną kadenciją iš eilės","Ne daugiau kaip tris kadencijas","Kadencijų skaičius neribotas"],"answer":0,"explain":"Konstitucijos 78 str. 2 d.: tas pats asmuo Respublikos Prezidentu gali būti renkamas ne daugiau kaip du kartus iš eilės."},
    {"q":"Kiek Konstitucinis Teismas turi teisėjų?","opts":["7","9","11","12"],"answer":1,"explain":"Konstitucijos 103 str. 1 d.: Konstitucinį Teismą sudaro 9 teisėjai."},
    {"q":"Kas tvirtina valstybės biudžetą?","opts":["Vyriausybė","Respublikos Prezidentas","Seimas","Lietuvos bankas"],"answer":2,"explain":"Konstitucijos 67 str. 14 p.: Seimas tvirtina valstybės biudžetą ir prižiūri jo vykdymą."},
    {"q":"Per kiek dienų Prezidentas turi pasirašyti įstatymą arba grąžinti jį Seimui?","opts":["Per 10 dienų","Per 7 dienas","Per 21 dieną","Per 14 dienų"],"answer":0,"explain":"Konstitucijos 71 str. 1 d.: Respublikos Prezidentas per 10 dienų po įstatymo pateikimo jį pasirašo arba grąžina Seimui."},
    {"q":"Kiek Seimo narių sudaro Seimą?","opts":["100","111","141","151"],"answer":2,"explain":"Konstitucijos 55 str. 1 d.: Seimą sudaro Tautos atstovai – 141 Seimo narys."},
    {"q":"Nuo kokio amžiaus Lietuvos piliečiai turi rinkimų teisę?","opts":["16 metų","18 metų","20 metų","21 metų"],"answer":1,"explain":"Konstitucijos 34 str. 1 d.: piliečiai, kuriems rinkimų dieną yra suėję 18 metų, turi rinkimų teisę."},
    {"q":"Nuo kokio amžiaus galima būti išrinktu Seimo nariu?","opts":["18 metų","21 metų","24 metų","25 metų"],"answer":2,"explain":"Konstitucijos 56 str. 1 d.: Seimo nariu gali būti renkamas pilietis, kuriam rinkimų dieną yra suėję 24 metai."},
    {"q":"Koks yra Seimo narių įgaliojimų laikas?","opts":["3 metai","4 metai","5 metai","6 metai"],"answer":1,"explain":"Konstitucijos 55 str. 2 d.: Seimo nariai renkami ketveriems metams."},
    {"q":"Kokia kalba yra valstybinė Lietuvoje?","opts":["Lietuvių","Lietuvių ir rusų","Lietuvių ir lenkų","Lietuvių ir anglų"],"answer":0,"explain":"Konstitucijos 14 str.: valstybinė kalba – lietuvių kalba."},
    {"q":"Koks yra Lietuvos valstybės herbas?","opts":["Gedimino stulpai","Vytis","Vilkas","Erelis"],"answer":1,"explain":"Konstitucijos 15 str.: Lietuvos valstybės herbas – Vytis."},

    # IV LYGIS — 2 ETAPAS
    {"q":"Konstitucijoje piliečiams laiduojama peticijos teisė reiškia:","opts":["teisę kreiptis į valdžios institucijas siūlant keisti teisės aktą","teisę kreiptis į Seimo kontrolierių","teisę kritikuoti valstybės įstaigų darbą","teisę kritikuoti savivaldybių darbą"],"answer":0,"explain":"Konstitucijos 33 str. 3 d.: peticijos teisė – kreiptis į valdžios institucijas siūlant keisti teisės aktus visuomenei svarbiu klausimu."},
    {"q":"Ar nuo to, pagal kurią Konstitucijos 89 str. dalį Seimo Pirmininkas pakeičia Prezidentą, priklauso jo pareigų apimtis?","opts":["Viskas priklauso nuo Prezidento sprendimo","Ne, nes Seimo pirmininkas negali spręsti užsienio politikos klausimų","Taip, nes pavaduodamas laikinai jis negali vykdyti kai kurių funkcijų","Ne, nes abiem atvejais jo pareigų apimtis vienoda"],"answer":2,"explain":"Pagal KT doktriną: kai Seimo Pirmininkas pavaduoja laikinai negalintį Prezidentą (89 str. 2 d.), negali atlikti visų Prezidento funkcijų."},
    {"q":"Kurios konstitucinės teisės ar laisvės yra absoliučios ir negali būti ribojamos?","opts":["Nė viena iš nurodytų","Žurnalisto teisė išsaugoti šaltinį","Teisė kreiptis į Konstitucinį Teismą","Ūkinės veiklos laisvė"],"answer":0,"explain":"Pagal KT doktriną: nė viena iš šių teisių nėra absoliuti – visos gali būti ribojamos įstatymu proporcingai."},
    {"q":"Kas gali laikinai pavaduoti savo pareigų negalintį eiti ministrą?","opts":["Ministro Pirmininko paskirtas kitas Vyriausybės narys","Respublikos Prezidento paskirtas kitas ministras","Kitas ministras paties ministro prašymu","Atitinkamas viceministras"],"answer":0,"explain":"Konstitucijos 98 str. 2 d.: Ministras Pirmininkas gali pavesti vienam iš ministrų laikinai pavaduoti kitą ministrą."},
    {"q":"Kuris teiginys neteisingas apie valdžios institucijų priimamus teisės aktus?","opts":["Respublikos Prezidentas priima įstatymus","Teismai priima nutartis, nuosprendžius, sprendimus","Seimas priima nutarimus ir kitus teisės aktus","Vyriausybė priima nutarimus ir kitus teisės aktus"],"answer":0,"explain":"Respublikos Prezidentas leidžia dekretus (85 str.), o ne įstatymus. Įstatymus priima Seimas."},
    {"q":"Ar galima apkalta už Seimo nario Seimo salėje pasakytus žodžius?","opts":["Ne, nes Konstitucija garantuoja saviraiškos laisvę","Taip, jei skatino visuomenės nesantaiką ir netoleranciją","Ne, nes indemnitetas yra neatsiejama Seimo nario statuso dalis","Taip, jei Seimo narys ką nors asmeniškai įžeidė"],"answer":1,"explain":"Pagal KT doktriną: apkalta galima, jei Seimo narys skatino nesantaiką ar netoleranciją – tai šiurkštus Konstitucijos pažeidimas."},
    {"q":"Kas priima sprendimus dėl gynybos nuo ginkluotos agresijos ir skelbia mobilizaciją?","opts":["Valstybės gynimo taryba","Lietuvos kariuomenė","Respublikos Prezidentas, o šiam negalint – Vyriausybė","Respublikos Prezidentas, kuris teikia sprendimus tvirtinti Seimui"],"answer":3,"explain":"Konstitucijos 142 str. 2 d.: Respublikos Prezidentas priima tokius sprendimus ir teikia juos tvirtinti artimiausiam Seimo posėdžiui."},
    {"q":"Koks teisės aktas minimas Konstituciniame akte Del nesijungimo i postsovietines Rytu sajungas?","opts":["1949 m. vasario 16 d. LLKS Tarybos deklaracija","1990 m. kovo 11 d. Nepriklausomybės aktas","1938 m. Lietuvos Konstitucija","1918 m. Laikinoji Konstitucija"],"answer":0,"explain":"Konstituciniame akte tiesiogiai minima 1949 m. vasario 16 d. Lietuvos Laisvės Kovos Sąjūdžio Tarybos deklaracija."},
    {"q":"Kuris subjektas turi teisę kreiptis į Konstitucinį Teismą prašydamas ištirti įstatymo atitiktį Konstitucijai?","opts":["Respublikos Prezidentas","Seimo kontrolierius","Savivaldybės meras","Lietuvos banko valdybos pirmininkas"],"answer":0,"explain":"Konstitucijos 106 str. 1 d.: kreiptis į Konstitucinį Teismą gali Seimas, Prezidentas, Vyriausybė ir teismai."},
    {"q":"Kurio teismo pirmininkas ir teisėjai gali būti pašalinti apkaltos tvarka?","opts":["Lietuvos vyriausiojo administracinio teismo","Apygardos teismo","Lietuvos apeliacinio teismo","Apylinkės teismo"],"answer":0,"explain":"Konstitucijos 74 str.: apkaltos procesas taikomas Aukščiausiojo Teismo ir Vyriausiojo administracinio teismo pirmininkams ir teisėjams."},
    {"q":"Lietuvos Respublikos piliečiai nuosavybės teise gali įsigyti:","opts":["žemės gelmes","vidaus vandenis ir miškus","dalį ekonominės zonos Baltijos jūroje","dalį kontinentinio šelfo"],"answer":1,"explain":"Konstitucijos 47 str.: vidaus vandenys ir miškai gali būti privačios nuosavybės objektai. Žemės gelmės, ekonominė zona ir šelfas – ne."},
    {"q":"Kuriam asmeniui Konstitucija garantuoja įstatymų leidybos iniciatyvos teisę?","opts":["Respublikos Prezidentui","Generaliniam prokurorui","Teisingumo ministrui","Konstitucinio Teismo pirmininkui"],"answer":0,"explain":"Konstitucijos 68 str. 1 d.: įstatymų leidybos iniciatyvos teisę turi Seimo nariai, Prezidentas, Vyriausybė ir piliečiai (50 000)."},
    {"q":"Konstitucinio Teismo pirmininką skiria:","opts":["Seimas Respublikos Prezidento teikimu","Respublikos Prezidentas Seimui pritarus","Seimas pasiūlius Seimo pirmininkui","Seimas Aukščiausiojo Teismo pirmininko teikimu"],"answer":0,"explain":"Konstitucijos 103 str. 3 d.: Konstitucinio Teismo pirmininką iš jo teisėjų skiria Seimas Respublikos Prezidento teikimu."},
    {"q":"Ar gali antrajame Seimo rinkimų ture varžytis trys kandidatai?","opts":["Taip, prieštarauja – visada turi būti du","Ne, neprieštarauja – jei Rinkimų kodekse numatyta","Ne, neprieštarauja – Konstitucija nereguliuoja balsų skaičiavimo","Taip, prieštarauja – lygių balsų atveju – pagal abėcėlę"],"answer":2,"explain":"Konstitucija nenustato konkrečios rinkimų sistemos ar balsų skaičiavimo taisyklių – tai reglamentuoja įstatymai."},
    {"q":"Ar 17 str. nuostata dėl Vilniaus kaip sostinės gali būti keičiama?","opts":["Taip, Seime du kartus su 3 mėn. pertrauka (2/3 balsų)","Taip, tik referendumu","Ne, negali būti keičiama","Taip, ne mažesne kaip 4/5 Seimo narių dauguma"],"answer":1,"explain":"Konstitucijos 148 str.: I skirsnio nuostatos (tarp jų 17 str.) gali būti keičiamos tik referendumu."},

    # III LYGIS — 1 ETAPAS
    {"q":"Kuriais žodžiais prasideda Konstitucijos preambulė?","opts":["Lietuvių Tauta","Lietuvos gyventojai","Piliečių bendruomenė","Lietuvos žmonės"],"answer":0,"explain":"Konstitucijos preambulė prasideda žodžiais: 'Lietuviu Tauta...'"},
    {"q":"Kaip buvo priimta Lietuvos Konstitucija?","opts":["Konstitucinio Teismo sprendimu","Vyriausybės nutarimu","Seimo nutarimu","Referendumu"],"answer":3,"explain":"Lietuvos Respublikos Konstitucija priimta 1992 m. spalio 25 d. referendumu."},
    {"q":"Kas riboja valdžios galias?","opts":["Teismas","Konstitucija","Susitarimas","Įstatymas"],"answer":1,"explain":"Konstitucijos 5 str. 2 d.: valdžios galias riboja Konstitucija."},
    {"q":"Kiek Seimo narių turi ratifikuoti sutartį, kad būtų galima keisti valstybės sienas?","opts":["1/2 visų Seimo narių","3/5 visų Seimo narių","2/3 visų Seimo narių","4/5 visų Seimo narių"],"answer":3,"explain":"Konstitucijos 67 str. 17 p.: sutartys dėl valstybės sienų keitimo ratifikuojamos 4/5 visų Seimo narių balsų dauguma."},
    {"q":"Kurios teisės piliečiams negarantuoja Konstitucija?","opts":["Vienytis į bendrijas ir asociacijas","Nemokamas aukštasis mokslas visiems","Turėti įsitikinimus ir juos laisvai reikšti","Rinktis į taikius susirinkimus be ginklo"],"answer":1,"explain":"Konstitucija garantuoja teisę į mokslą, bet nemokamas aukštasis mokslas visiems negarantuojamas – prieinamas pagal gebėjimus (41 str.)."},
    {"q":"Kiek metų renkamas Respublikos Prezidentas?","opts":["3 metams","4 metams","5 metams","6 metams"],"answer":2,"explain":"Konstitucijos 78 str. 1 d.: Respublikos Prezidentas renkamas penkeriems metams."},
    {"q":"Nuo kokio amžiaus galima būti išrinktam Respublikos Prezidentu?","opts":["30 metų","35 metų","40 metų","45 metų"],"answer":2,"explain":"Konstitucijos 78 str. 1 d.: Prezidentu gali būti renkamas pilietis, kuriam ne mažiau kaip 40 metų."},
    {"q":"Kokia yra Seimo sesijų tvarka?","opts":["Viena sesija per metus","Dvi sesijos – pavasario ir rudens","Trys sesijos per metus","Seimas dirba nuolat be sesijų"],"answer":1,"explain":"Konstitucijos 64 str. 1 d.: Seimas kasmet renkasi į dvi eilines sesijas – pavasario (kovo 10 d.) ir rudens (rugsėjo 10 d.)."},
    {"q":"Kas skelbia Lietuvos Respublikos įstatymus?","opts":["Seimo Pirmininkas","Respublikos Prezidentas","Ministras Pirmininkas","Konstitucinis Teismas"],"answer":1,"explain":"Konstitucijos 70 str.: Seimo priimtus įstatymus pasirašo ir oficialiai paskelbia Respublikos Prezidentas."},
    {"q":"Per kiek laiko sulaikytas asmuo turi būti pristatytas į teismą?","opts":["48 valandas","12 valandų","72 valandas","24 valandas"],"answer":0,"explain":"Konstitucijos 20 str. 3 d.: sulaikytasis ne vėliau kaip per 48 valandas turi būti pristatytas į teismą."},
    {"q":"Koks yra Vyriausybės įgaliojimų laikas?","opts":["4 metai (Seimo kadencija)","Iki naujo Seimo pirmojo posėdžio","5 metai (Prezidento kadencija)","Iki Prezidento rinkimų"],"answer":1,"explain":"Konstitucijos 92 str. 4 d.: Vyriausybė grąžina savo įgaliojimus naujai išrinktam Seimui po jo pirmojo posėdžio."},
    {"q":"Kiek laiko Konstitucinio Teismo teisėjai eina pareigas?","opts":["5 metai","7 metai","9 metai","12 metų"],"answer":2,"explain":"Konstitucijos 103 str. 2 d.: Konstitucinio Teismo teisėjai skiriami 9 metų kadencijai."},
    {"q":"Kas yra teisingumo vykdymo šaltinis Lietuvoje?","opts":["Konstitucinis Teismas","Aukščiausiasis Teismas","Tik teismai","Generalinė prokuratūra"],"answer":2,"explain":"Konstitucijos 109 str. 1 d.: teisingumą Lietuvos Respublikoje vykdo tik teismai."},
    {"q":"Kokia yra Konstitucijos vieta teisinių aktų hierarchijoje?","opts":["Lygiavertė tarptautinėms sutartims","Aukščiausia – negalioja joks jai prieštaraujantis aktas","Aukštesnė už įstatymus, bet žemesnė už tarptautines sutartis","Žemesnė už ES teisę"],"answer":1,"explain":"Konstitucijos 7 str. 1 d.: negalioja joks įstatymas ar kitas teisės aktas, priešingas Konstitucijai."},
    {"q":"Kiek reikia Seimo narių balsų pakartotinai priimti Prezidento grąžintą įstatymą?","opts":["Daugiau kaip pusė visų Seimo narių","2/3 visų Seimo narių","3/5 visų Seimo narių","Absoliuti dauguma posėdyje dalyvavusių"],"answer":1,"explain":"Konstitucijos 72 str. 2 d.: pakartotinai priimti įstatymą – ne mažiau kaip 2/3 visų Seimo narių balsų dauguma."},

    # II LYGIS — papildomos
    {"q":"Kam priklauso Suverenitetas?","opts":["Tautai","Gyventojams","Piliečiams","Žmonėms"],"answer":0,"explain":"Konstitucijos 2 str.: Lietuvos valstybę kuria Tauta. Suverenitetas priklauso Tautai."},
    {"q":"Kuris teiginys teisingas apie Vilnių?","opts":["Vilnius – Gedimino įkurta sostinė","Vilnius – tradicinė sostinė","Vilnius – nuolatinė sostinė","Vilnius – ilgaamžė istorinė sostinė"],"answer":3,"explain":"Konstitucijos 17 str.: Vilniaus miestas – ilgaamžė istorinė Lietuvos sostinė."},
    {"q":"Kuris teiginys teisingas apie įstatymo nežinojimą?","opts":["Suteikia papildomų garantijų","Atleidžia nuo atsakomybės","Neatleidžia nuo atsakomybės","Leidžia nevykdyti įstatymo"],"answer":2,"explain":"Konstitucijos 7 str. 2 d.: įstatymų nežinojimas neatleidžia nuo atsakomybės."},
    {"q":"Kuris teiginys teisingas apie žmogaus teises?","opts":["Žmogaus teisės ir laisvės yra prigimtinės","Yra paveldimos","Suteikiamos gimstant","Suteikiamos valstybės"],"answer":0,"explain":"Konstitucijos 18 str.: žmogaus teisės ir laisvės yra prigimtinės."},
    {"q":"Koks yra Konstitucinio Teismo sprendimų pobūdis?","opts":["Rekomendacinio pobūdžio","Galutinis ir neskundžiamas","Skundžiamas Aukščiausiajam Teismui","Privalomas tik Seimui"],"answer":1,"explain":"Konstitucijos 107 str. 2 d.: Konstitucinio Teismo sprendimai yra galutiniai ir neskundžiami."},
    {"q":"Kas yra vykdomoji valdžia Lietuvoje?","opts":["Seimas","Vyriausybė","Konstitucinis Teismas","Respublikos Prezidentas"],"answer":1,"explain":"Konstitucijos 5 str. 1 d. ir 91 str.: vykdomąją valdžią vykdo Vyriausybė."},
    {"q":"Koks yra savivaldybių tarybų narių įgaliojimų laikas?","opts":["2 metai","3 metai","4 metai","5 metai"],"answer":2,"explain":"Konstitucijos 119 str. 2 d.: savivaldybių tarybos renkamos ketveriems metams."},
    {"q":"Kas gina Lietuvos nepriklausomybę ir teritorinį vientisumą?","opts":["Tik profesinė kariuomenė","Tik NATO sąjungininkai","Kiekvienas Lietuvos pilietis","Tik Krašto apsaugos ministerija"],"answer":2,"explain":"Konstitucijos 139 str. 1 d.: Lietuvos valstybės gynimas nuo užsienio ginkluoto užpuolimo – kiekvieno piliečio teisė ir pareiga."},
    {"q":"Kaip valstybėje nustatoma bažnyčių ir religinių organizacijų būklė?","opts":["Įstatymu","Susitarimu ir Konstitucija","Konstitucija","Vyriausybės nutarimu"],"answer":0,"explain":"Konstitucijos 43 str. 3 d.: valstybė ir bažnyčia atskirtos; bažnyčių būklę nustato įstatymas."},
    {"q":"Kas priima sprendimą dėl Lietuvos narystės tarptautinėse organizacijose?","opts":["Respublikos Prezidentas","Vyriausybė","Seimas","Užsienio reikalų ministras"],"answer":2,"explain":"Konstitucijos 67 str. 16 p.: Seimas ratifikuoja ir denonsuoja tarptautines sutartis, sprendžia narystės klausimus."},
    {"q":"Nuosavybė pagal Konstituciją:","opts":["Absoliučiai neliečiama","Tik valstybės nuosavybė saugoma","Neliečiama, bet gali būti paimta visuomenės poreikiams teisingai atlyginus","Žemesnė už valstybės interesus visais atvejais"],"answer":2,"explain":"Konstitucijos 23 str.: nuosavybė neliečiama, tačiau visuomenės poreikiams ji gali būti paimta tik įstatymo pagrindu ir teisingai atlyginus."},
    {"q":"Koks yra Ministro Pirmininko skyrimo procesas?","opts":["Seimas skiria Prezidento teikimu","Prezidentas skiria Seimui pritarus","Prezidentas skiria savarankiškai","Seimas skiria savo iniciatyva"],"answer":1,"explain":"Konstitucijos 92 str. 1 d.: Ministrą Pirmininką skiria Respublikos Prezidentas, gavęs Seimo pritarimą."},
    {"q":"Kaip vadinama Lietuvos valdymo forma?","opts":["Konstitucinė monarchija","Parlamentinė respublika","Pusiau prezidentinė respublika","Prezidentinė respublika"],"answer":2,"explain":"Lietuva – pusiau prezidentinė (mišri) respublika: prezidentas turi reikšmingą vaidmenį, tačiau Seimas taip pat kontroliuoja vykdomąją valdžią."},
    {"q":"Kiek parašų reikia surinkti piliečių įstatymų leidybos iniciatyvai?","opts":["10 000","30 000","50 000","100 000"],"answer":2,"explain":"Konstitucijos 68 str. 2 d.: įstatymų leidybos iniciatyvos teisę turi 50 000 piliečių, turinčių rinkimų teisę."},
    {"q":"Kiek kartų iš eilės tas pats asmuo gali būti renkamas Respublikos Prezidentu?","opts":["Vieną kartą","Du kartus","Tris kartus","Neribotą kartų skaičių"],"answer":1,"explain":"Konstitucijos 78 str. 2 d.: tas pats asmuo Respublikos Prezidentu gali būti renkamas ne daugiau kaip du kartus iš eilės."},
    {"q":"Kokiomis sąlygomis gali būti įvestas nepaprastasis (karo) padėties režimas?","opts":["Vyriausybės sprendimu","Prezidento sprendimu su nedelsiant teikiamu Seimo pritarimu","Seimo sprendimu","Konstitucinio Teismo leidimu"],"answer":1,"explain":"Konstitucijos 142 str. 1 d.: karo padėtį įveda Respublikos Prezidentas, nedelsiant teikdamas šį sprendimą Seimui."},
]


# ─── Состояние пользователей ──────────────────────────────────────────────────
user_state = {}


def new_quiz(user_id, count=20):
    pool = QUESTIONS.copy()
    random.shuffle(pool)
    user_state[user_id] = {
        "questions": pool[:count],
        "index": 0,
        "score": 0,
    }
    return user_state[user_id]


def get_state(user_id):
    if user_id not in user_state:
        user_state[user_id] = {"questions": [], "index": 0, "score": 0}
    return user_state[user_id]


# ─── Отправить вопрос ─────────────────────────────────────────────────────────
async def send_question(target, context, state, edit=False):
    idx = state["index"]
    total = len(state["questions"])
    q = state["questions"][idx]

    text = f"❓ *Klausimas {idx + 1} / {total}*\n\n{q['q']}"
    buttons = [[InlineKeyboardButton(f"{chr(65+i)}. {opt}", callback_data=f"ans_{i}")]
               for i, opt in enumerate(q["opts"])]
    markup = InlineKeyboardMarkup(buttons)

    if edit:
        await target.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")
    else:
        msg = target.message if hasattr(target, "message") else target
        await msg.reply_text(text, reply_markup=markup, parse_mode="Markdown")


# ─── Команды ──────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    state = new_quiz(uid, count=20)
    await update.message.reply_text(
        f"🇱🇹 *Konstitucijos egzamino treniruoklis*\n\n"
        f"Банк: *{len(QUESTIONS)} вопросов* из реальных тестов IV, III и II уровней.\n"
        f"Каждый раз — случайные *20 вопросов*.\n"
        f"После каждого ответа — объяснение со ссылкой на статью.\n\n"
        f"Цель: 85%+ = сдал ✅\n\nПоехали! 💪",
        parse_mode="Markdown"
    )
    await send_question(update, context, state)


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


# ─── Ответ на вопрос ──────────────────────────────────────────────────────────
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = update.effective_user.id
    state = get_state(uid)
    if not state["questions"]:
        await query.edit_message_text("Spustelėk /start pradėti testą.")
        return

    chosen = int(query.data.split("_")[1])
    idx = state["index"]
    q = state["questions"][idx]
    correct = q["answer"]

    opts_text = ""
    for i, opt in enumerate(q["opts"]):
        if i == correct and i == chosen:
            opts_text += f"✅ *{chr(65+i)}. {opt}*\n"
        elif i == correct:
            opts_text += f"✅ *{chr(65+i)}. {opt}*\n"
        elif i == chosen:
            opts_text += f"❌ {chr(65+i)}. {opt}\n"
        else:
            opts_text += f"▫️ {chr(65+i)}. {opt}\n"

    if chosen == correct:
        state["score"] += 1
        result = "✅ *Teisingai!*"
    else:
        result = f"❌ *Neteisingai.* Teisingas: *{chr(65+correct)}*"

    explain = f"\n\n📖 _{q.get('explain', '')}_" if q.get("explain") else ""

    state["index"] += 1
    total = len(state["questions"])

    if state["index"] < total:
        btn = [[InlineKeyboardButton("➡️ Kitas klausimas", callback_data="next")]]
    else:
        btn = [[InlineKeyboardButton("🔄 Pradėti iš naujo", callback_data="restart")]]

    await query.edit_message_text(
        f"❓ *Klausimas {idx+1}*\n_{q['q']}_\n\n{opts_text}\n{result}{explain}",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode="Markdown"
    )


async def handle_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    state = get_state(uid)

    if state["index"] >= len(state["questions"]):
        score = state["score"]
        total = len(state["questions"])
        pct = round(score / total * 100)
        verdict = ("🎉 *Puikiai! Egzaminą išlaikytumėte!*" if pct >= 85
                   else "👍 *Gerai, bet dar reikia tobulinti.*" if pct >= 70
                   else "📚 *Reikia daugiau pasipraktikuoti.*")
        await query.edit_message_text(
            f"🏁 *Тест завершён!*\n\nРезультат: *{score}/{total}* ({pct}%)\n\n{verdict}\n\n"
            f"Нажми /start чтобы пройти заново с новыми вопросами.",
            parse_mode="Markdown"
        )
        return

    await send_question(query, context, state, edit=True)


async def handle_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    state = new_quiz(uid, count=20)
    await query.edit_message_text(
        f"🔄 Новый тест — {len(state['questions'])} случайных вопросов!\n\nПоехали! 💪",
        parse_mode="Markdown"
    )
    await send_question(query, context, state, edit=False)


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в .env файле!")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^ans_"))
    app.add_handler(CallbackQueryHandler(handle_next, pattern="^next$"))
    app.add_handler(CallbackQueryHandler(handle_restart, pattern="^restart$"))
    print(f"✅ Бот запущен! Вопросов в банке: {len(QUESTIONS)}")
    app.run_polling()


if __name__ == "__main__":
    main()
