import matplotlib.pyplot as plt
from numpy import array
import matplotlib.collections as collections

maxNumTrainingIterations = 40
numRealIterations = 15


GIMMEGridabilities = [0.7609962427767953, 0.777731185851694, 0.7921500077229829, 0.7973433532752835, 0.8023439549501399, 0.8064611971834807, 0.8071110211467193, 0.8096119712003301, 0.809878029477386, 0.8092655485901219, 0.8122477754734897, 0.8124337225985346, 0.8129143067062736, 0.8136802265690863, 0.8124363864883181, 0.8144864900394144, 0.8148100482649584, 0.8138015572749482, 0.8148489008978247, 0.8151121102708213, 0.8150025374651624, 0.8147055456297243, 0.8169715691981814, 0.8151717614710838, 0.8157457847253108, 0.8171234796837642, 0.8160374862646537, 0.8158674356270773, 0.8167577019281214, 0.8169664499381095, 0.817833822624188, 0.8161925554387912, 0.8166804216231132, 0.8172161198552197, 0.8164098506007481, 0.8160015452928879, 0.8157337422582145, 0.8175292688229747, 0.8176410479390384, 0.8168562455646807, 0.7889930715941604, 0.7872865554741634, 0.7905007480432932, 0.7904050770914254, 0.7909633327253373, 0.7922787645676286, 0.7952919382926449, 0.797505872524637, 0.798271729595611, 0.8001787435977281, 0.8000570253719511, 0.8020469786658462, 0.8045520364790916, 0.8045934743922935, 0.8050944474442243]
GIMMEGridengagements = [0.5816611940928529, 0.6071723706374407, 0.6300752195606129, 0.6384150271861245, 0.6458492591212897, 0.6528783860337979, 0.6534723044611613, 0.6584319726606538, 0.6585941428394749, 0.6575493494688386, 0.6616639854961508, 0.6619078891630058, 0.6630017606856806, 0.6644500379639321, 0.6626581101622222, 0.6657304784562142, 0.6659257108009914, 0.6650173552447947, 0.6661187466278161, 0.665941133075651, 0.6662668794166888, 0.6655924781702485, 0.6690561847782254, 0.6668431414780928, 0.6673703523128476, 0.6684466636447013, 0.668446150278384, 0.6683204225364494, 0.6696440075734458, 0.6691098628189702, 0.6712769619067604, 0.6686142933117911, 0.6687946941276876, 0.6697866488561514, 0.6682950468299357, 0.6680107430755928, 0.6676071212156326, 0.670228144956923, 0.6707126516155524, 0.6692533928433446, 0.6256266455588558, 0.62288868621675, 0.6281956320182711, 0.6273684856670297, 0.628587130036748, 0.6303808959623824, 0.6351823741822351, 0.6385968099942846, 0.6402033712659464, 0.6423905648956284, 0.6426205110555848, 0.6458761295681723, 0.6500934799929203, 0.6497820107865642, 0.651219789434489]
GIMMEGridprofDiffArray = [0.7754501176992531, 0.7829698717204323, 0.7374387346763385, 0.722292071140856, 0.7075189310274047, 0.6935033198363508, 0.6929928733484815, 0.6826139843419036, 0.6827946437759137, 0.6850112793118657, 0.6762389094258773, 0.6761585476037899, 0.6738813342578296, 0.6709474738323195, 0.6748724036546843, 0.6682156358987236, 0.6681280276248853, 0.6700609058847444, 0.6676465708093191, 0.6681364300120805, 0.6674319520780875, 0.6688860332643922, 0.6615230297479752, 0.6665466689701366, 0.6652037994969646, 0.6629933767809255, 0.6631077534817895, 0.6633723894262504, 0.6605726601123693, 0.6618365001256834, 0.6572179604930225, 0.6630516942811507, 0.6623916221850573, 0.6603222860004921, 0.6635669170797303, 0.6640084405597981, 0.664828244080311, 0.6592678128502291, 0.6585236960679794, 0.6616468204998593, 0.7533389980701296, 0.7545108338130359, 0.7430501100896113, 0.7453500967029164, 0.7426974615717997, 0.7390493906093791, 0.729129832875544, 0.7224469657154257, 0.7194241457552975, 0.7149886393003602, 0.7147347730298902, 0.7079050441781151, 0.6993691083905066, 0.7004687646591206, 0.6974090760101851]

GIMMEabilities = [0.7599093400648075, 0.7815560883302207, 0.7934063192470684, 0.8002079307424342, 0.80226291712822, 0.8068993268127654, 0.8095765772705092, 0.809861364187284, 0.8114394217522506, 0.8116880447205123, 0.8122483240581616, 0.813676605206286, 0.8166546912179025, 0.8146543307171116, 0.8152432055210236, 0.8160135129506975, 0.8173238232638226, 0.8148616483391, 0.8167599905456592, 0.8179369992013925, 0.8175650358661156, 0.8174962555980811, 0.8178982524183216, 0.8171546937648261, 0.8178127265282055, 0.8168786924717706, 0.818749731857578, 0.817712907530222, 0.8181080415787374, 0.8176238715402645, 0.8188613469990655, 0.8193407505262098, 0.8181881397956091, 0.8187880496467885, 0.818073886007926, 0.8181782057877812, 0.8186893901204455, 0.8182819873854353, 0.8190014935028617, 0.8189661936545859, 0.7890146140870776, 0.7905972343629287, 0.7917519382630525, 0.7912595556862494, 0.7944115458151859, 0.7933706034059732, 0.7929442941450633, 0.7972222208755071, 0.7971262039429795, 0.8011894330665316, 0.8021065143847008, 0.8015020673101835, 0.8042305132288949, 0.8047940109619773, 0.8067692804877014]
GIMMEengagements = [0.578457197023491, 0.6119419533263389, 0.6301489125906069, 0.6411207763827097, 0.6444069606152644, 0.6513842932507448, 0.6556795400127977, 0.6554874372324269, 0.6582105201886487, 0.6588424813937522, 0.6593551007240522, 0.6625354466664364, 0.6672293327962243, 0.6639653738085419, 0.6652229749462347, 0.6658446524366062, 0.6675972363156282, 0.6644995542790436, 0.6673216492236371, 0.6690338653669939, 0.6682999703973276, 0.6687013101074842, 0.6689119959487957, 0.6678786300075682, 0.6687739841035684, 0.6677862216546544, 0.6703963857814245, 0.6690385996548246, 0.668827852717281, 0.6693180898781076, 0.6704521201420287, 0.6712579361621314, 0.668887291270817, 0.6710629110699778, 0.6692215248993012, 0.6701056537945594, 0.6702445015066532, 0.6701499030813429, 0.6704689270156026, 0.670890549053249, 0.6234487712909133, 0.6258309134673722, 0.6279415461551799, 0.6264591215457966, 0.6318578157166398, 0.6307433461880655, 0.6295505280268991, 0.6366882233011046, 0.6364387785031785, 0.6426794424630651, 0.644204766962626, 0.6430611301487241, 0.6471445079072661, 0.6486699494886076, 0.6511382925157666]
GIMMEprofDiffArray = [0.7821953746873925, 0.7725913821575497, 0.7377856527909636, 0.7166035142038267, 0.7108401646397318, 0.6964969574316179, 0.6881887887362962, 0.6890453468804517, 0.6832923193115223, 0.6822485149803733, 0.6812358386223901, 0.6745943334100329, 0.6650472411307262, 0.6724128270131924, 0.6694216710404024, 0.6682452553909632, 0.6646210448551602, 0.6713269632352395, 0.6650596389269855, 0.6617520359877658, 0.6634773113074108, 0.6625551334997448, 0.6621538306454265, 0.6643515153470964, 0.6623577839932839, 0.6645315316853138, 0.6589324743185326, 0.6620657255457875, 0.6623664784536007, 0.6613122163321186, 0.6589763881092168, 0.6573993049367804, 0.662474959025869, 0.6576451652496078, 0.6617507803246286, 0.6596956262113781, 0.6594963814380471, 0.6597101515662956, 0.6590285645020286, 0.6581745206263808, 0.7580963287615803, 0.7480874212572062, 0.7438947358277661, 0.74723780160413, 0.7357160849697907, 0.7386306202058238, 0.7410245037526382, 0.725872217053139, 0.7271487003407943, 0.7139842030780968, 0.7114299056011112, 0.7139981225250621, 0.7052811549477314, 0.7024995282247478, 0.6974635893866651]

Randomabilities = [0.7616127600746102, 0.7819764780199744, 0.7819787801892694, 0.7831889889873713, 0.7839948111854663, 0.782810354031018, 0.7822930662335247, 0.7817302419804995, 0.7816630937695077, 0.7829187394153183, 0.7806546462488789, 0.7819716763395285, 0.7803699422240555, 0.779931865864461, 0.7835870853010432, 0.781631247647044, 0.7826794268900791, 0.7831371753065404, 0.7815678991739438, 0.7819696271141071, 0.7829594716812805, 0.7815663234562509, 0.7835076122011408, 0.7810403314848833, 0.7826700546267894, 0.7827625446790133, 0.7820739561815624, 0.7840139961421354, 0.7812734442946581, 0.7838419882529513, 0.7817942109119841, 0.7821887460770028, 0.7812512643648685, 0.782265824060475, 0.7818668964301222, 0.7823185754684946, 0.7811839522851147, 0.7829694538977007, 0.7818838556972012, 0.7839958376981978, 0.7801191195549266, 0.7810785029381291, 0.7820251745626435, 0.7841386803808491, 0.7817836111976422, 0.7813141286726795, 0.7827262312005492, 0.781740819767028, 0.7794935240230659, 0.7802716985575482, 0.7814924468405237, 0.7817697765410804, 0.7819475008637139, 0.7826524470878704, 0.7807409457829174]
Randomengagements = [0.579464928919271, 0.6118556663224993, 0.6112369966989636, 0.6138988177796489, 0.6143877896612482, 0.6130955916461586, 0.6118016066492288, 0.6110064053177904, 0.6101466784274747, 0.6127889993003615, 0.609603043228332, 0.6113390325113697, 0.6089266856944402, 0.6085780574090371, 0.6138518948078899, 0.6111134592023703, 0.6126910127551013, 0.613790378956792, 0.6110102076616439, 0.611457535139219, 0.6132402403995941, 0.6107984972024799, 0.6144972711606324, 0.6103064986454246, 0.6126888571918587, 0.612838848877857, 0.6114986706332765, 0.6141519444040288, 0.6104847261480093, 0.614261376280578, 0.6108905276319618, 0.6108533136166574, 0.6104840106460996, 0.6119544725154424, 0.6117552727854306, 0.6119514961485337, 0.6100601074371208, 0.6125516232968922, 0.6114947508953784, 0.6150438819188045, 0.6085024989994817, 0.6100039442229397, 0.6116259343029832, 0.6145144272133638, 0.6105135751144749, 0.6107611012001054, 0.6122779970529472, 0.6108446765726043, 0.6076134913463731, 0.6088925623129513, 0.6104469014005839, 0.6111259194904243, 0.611590447973666, 0.6125140297116941, 0.6095014087494164]
RandomprofDiffArray = [0.7800738338541666, 0.7728791160493987, 0.777591129720335, 0.771922172748005, 0.7711729499531251, 0.7739448375513728, 0.7765329956485857, 0.7780708947677317, 0.7797971407124556, 0.7741438623600235, 0.7811292773403955, 0.7771391992632533, 0.7824005598550016, 0.782880582896174, 0.7717410696053882, 0.7780613379747884, 0.77445191622109, 0.7723035193283447, 0.7782722342867321, 0.7770378426186648, 0.7733318660155051, 0.7786600311947341, 0.7706161130515629, 0.7798281366581193, 0.7743715110324475, 0.7743065136457492, 0.7771437301276161, 0.771416819216074, 0.779416570678309, 0.7710797053196224, 0.7785737709096145, 0.7782972900314534, 0.7790708527047027, 0.7759362695091823, 0.7765104228217768, 0.7760763526120741, 0.7800788786743311, 0.7746344885788768, 0.7771217479357204, 0.7695386434230823, 0.783683568624122, 0.7798340646884881, 0.7765773955961357, 0.7706670936879707, 0.7793939920972467, 0.7784517422223542, 0.7752843326464425, 0.7784615226948277, 0.7851131420679084, 0.7820802363249886, 0.7789425825580254, 0.7776766854307473, 0.776770206317592, 0.7748747214462883, 0.7813143004971939]


timesteps=[i for i in range(maxNumTrainingIterations + numRealIterations)]
empConvValue=[0.8518004375307543 for i in range(maxNumTrainingIterations + numRealIterations)]

plt.rcParams.update({'font.size': 22})

fig = plt.figure()
ax = fig.add_subplot(111)
c1 = collections.BrokenBarHCollection([(0,40)], (0.74,0.12), facecolor='#f7e4d4', alpha=0.5)
c2 = collections.BrokenBarHCollection([(40,15)], (0.74,0.12), facecolor='#bdedcf', alpha=0.5)
ax.add_collection(c1)
ax.add_collection(c2)

plt.plot(timesteps, GIMMEGridabilities, label=r"GIMME Grid strategy")
plt.plot(timesteps, GIMMEabilities, label="GIMME strategy")
plt.plot(timesteps, Randomabilities, label="Random strategy")
plt.plot(timesteps, empConvValue, linestyle= "--", label="\"Perfect Information\" convergence value")
plt.xlabel("Iteration", fontsize=30)
plt.ylabel("avg. Ability Increase", fontsize=30)
plt.legend(loc='best', fontsize=20)

plt.show()


empConvValue=[0.5511328170913202 for i in range(maxNumTrainingIterations + numRealIterations)]

plt.plot(timesteps, GIMMEGridprofDiffArray, label="GIMME Grid strategy")
plt.plot(timesteps, GIMMEprofDiffArray, label="GIMME strategy")
plt.plot(timesteps, RandomprofDiffArray, label="Random strategy")
plt.plot(timesteps, empConvValue, linestyle= "--", label="\"Perfect Information\" convergence value")
plt.xlabel("Iteration", fontsize=30)
plt.ylabel("avg. Preference Differences", fontsize=30)
plt.legend(loc='best', fontsize=20)

plt.show()
