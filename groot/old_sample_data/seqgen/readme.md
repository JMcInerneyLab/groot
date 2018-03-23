# Sample data #3 - seqgen generated sequences

## The tree
```ascii
          |-[C]
    |-<B>-|
    |     |-[D]
<A>-|
    |     |-[F]
    |-<E>-|
          |           |-[I]
          |     |-<H>-|
          |     |     |     |-[M]
          |     |     |-<L>-| 
          |     |           |-[N]
          |-<G>-|
                |     |-[K]
                |-<J>-|
                      |     |-[P]
                      |-<O>-|
                            |-[Q]
```

Where `<A>` can be rooted on an "outgroup" `<W>`.

## The composite mapping is
The 
`X<G>` & `Y<J>` = `1ST_ANCESTOR_OF Z<A>`

## Source data
```newick
(((C:1,D:1)B:1,(F:1,((I:1,(M:1,N:1)L:1)H:1,(K:1,(P:1,Q:1)O:1)J:1)G:1)E:1)A:1,W:1):1
```

```fasta
#NEXUS
[
Generated by seq-gen Version 1.3.2x

Simulations of 10 taxa, 200 amino acids
  for 1 tree(s) with 1 dataset(s) per tree

Branch lengths of trees multiplied by 4

Rate homogeneity of sites.
Model = GENERAL: General time reversible (amino acids)
]

 18 200
11	NDKGKKSKKEMQGTQVGHLAYCPRKVGTTSNSDSGAECAADDTGQLRPGRLGGWDQRIHPINITVSSALELARLVADYDEWIEFSIGAENNASHDFFNSIIVVPILMVLPAEFIIGLFTKGKCKRNLRELLFLGAQADYMEHQSDSRQVAGKVRHKFLILKEYPRLAQYADRIVLNTVMTFYAPTSPEELVEVTLVMSPT
12	NDKGFKSKKEDQKSQVGHVAYCARKVGTTQNSEPGAECAAGDPGQPRKGRVGGWDQRIHPINITVSSALELARFVADYDEWIEFSIGAWNNRSHVFWNSIGVVKILWTLPAEFIIALFTGGKAKGSKRELLMLGAQALNMEHQHDSRQVAGKVDHKFLIKKEYWRLAQYADRIWINTVMTFYAPTSWEEPVENKMVCSPT
13	CDKLFKSKKEQQKSQVGHVAYCASKKGTTNNSEPPAESFAGDPGQPRKGRLCGRDQRIKPIYTPVSSALELARFQADYDEWIEMSIGAEWNRSRVFWLPIWVIKILWTLPAEFIIALFTGGKAKGSKMELLMNGYQALNMEHQHDQRQVAGKVEHKFAWKKEYWWLAQYYDRIRINTVMTFSAPGSEEYPVENKMVCSPL
C	TDVLFGHKKEQQKLCVGHTAYCASKRTTTNNSEPPRHTFCGDPGQPRKGRDCGRDQRIKPIATPGSSALELARFVFDRDEPLEMQIGAEWNRSWVLWLPTWVIKILWTLPANFIIALPTIGKAKGSQMELLMNGYQALNMEAQFNQRQVAGKTHHKFMTLKEYAWLKPMYDISRINLVMTFSAPGEEEYPVENKAVCSHL
D	CDYLFPDCKEQQKNQVGHVAYMLSKKGTTNNSEPPTESFAGDPGKSRKGRLDHVDQRKKPIYTMTSSALELASFTADYDLWITMSIGAEWNRSRVFWLIIWVIKILWTLPAEFIIALVTGGKYNGSKMHALEAKYIALQMEHQHDQRQVAGKVEHKRAWKVEYWWLAQYYARIWINTVMEGSAPGSEENPVENWMVMSPL
14	NQKGFKSKDEDNKAVVGANAYCARKVGTTQNSEPGAEPAAGVSTQPRKGRVGGWDQRIHPINITVSSYLELARFMADTDEWIEESIGATPNRSHVFNNSDGVVKILWTIDAEFYIALFTGGKAFGSKRELLMHKAPALTMEHQHSSRQVAGKRDHKFLIKKEYRRLASYADRRWPNTVMTFGAPTMHEEPVPNKMVCRPT
F	NQKGFKSKDEDNKAVVGANAYCANEVGTHQNSEPMNEPAAGTSTQPRKGRVGGHDQRIHPMNITVSSYLELARFMADTDENIEESLGATPQRVHVFNNSDGVVPIMWTIDAEFYIDLFTGAKANGSLRELIMHKAHALTMEHQHDSRQEAGKRPHKFLIKKEYRRLASYADRRWPNTVMTFGAPTMHEHPVPNTMVCCPT
15	NQFGNTSKDEDNKAVVGANAYMARKVVTTQNSEPGLQPAAGVSTQHRDGRVGGWDQRIHPFNITVQSYLELARFMAHETECIEESIGYTPNRCKVFKDSDGVVKILWKIAALFYIALFTRGKAFGQKRELLAHKANALTMMHQHSSRQVAGKRDHKFLIKKEYRRRASYTDRRWPNCVMHFGRCTMHEEPWYNKMVCRPT
16	NQTGNTSKDEDNKAVWGANAKMARHVVITQNSEDGLQPAAGNSTQHADGRVHMWDQVIHPFNITVMSTLELQRFMFHECECWEESIGHTMWRCKVFKDTDGVVKPLAEIAALFYIALFTRGKAFGPKRELLAHKANALTMMHDHSSRQVDGKIGHKFLIKKHYRRRASYFDRRWPNCVMPFGSCTMHEENWYNQGVGRPT
I	NQRNNISWPEDNFLVYGAMSVMARHWVITSNSEDLLQMAAGSSTQKADGRTHMWPQVIHPFNIYVMCTLELQRFMFHNCECWEESIGHTMWRCKGFFDTRGVVYPLLEIYALEYIALFTRGKAFGPRRELLAHKANMDTMMHDHSIRQVHWKWGHKFLIKKHYRRTPSYFNRQKPACVMPFWACTMHEENWDGQGVGRPT
17	NLVGFHSKDEDNKAVWGANAKHEDHVVVNLNSEDGLQPAAGNSTQKSCGRVHMTDQVMHPFNITTMVTLELQRFMSHECECWEESSGHTVYRCKVFNDTDGVVKPDAEIASLFIICLFTRGKFFGPKRELCAHKANALTGMHDHCSRQVPGDIGHKFLIKKHYRRRGSYFDRRWPNDVMPFGSCTMHECNWYNQGVGRPT
M	NLVGFHSKDEDNKIVWGANAKHEDHVVVVLNSEDGLQPYAGNSQQKSCGKVHMTDQVFHIFNHTTMVTLELSRFMSTEVECAEESSCHTRKRCKVFKDTDGVVKPDAEIASLFIICLFTRGKFFGPKRELCAMKANGSTSMHDHDKRQVHGDIGHKFLIKKHERRRHSPFCRRPPFDVAPFGSETMYFCNWYNTNVGRPY
N	NLVGFHSKDEDQKAVDGGNAKPEDHVVVNLYQEDGLQPAAGNSTMASCGRVHMTGQVMHPFNITTMVTLENSRFMSHECECIEESSGHTVYRCKVFNDYDNVDKPDAEIASLFQICLFTRGKPFCPKRELCIWKANALTGMVDVCSEVYPGDIGHKFLIKKHYRPRGLHRFRRWPHDVMPFWSCTMHHCNWYNQAVGRPM
18	NQFGNTWKPEDNKPSVGANAHWARKKVTTQNSERQLQPSDGVSTQHRDGRGGGWMQRKHPFNFTVCAYNEFARFMAHETQCIENTIGYTPNRCKKFHDSVGVVKILWKQAKLEYIALFTRGHAFGQKRELQAHKAVALTMMHQTSSRQVAGKRDHNFLIKKEYRNRASYTARRWRNCVMHFWRCTMHEEPTYNCRVCRWT
K	NVRGNTWKPEDNKPSVGANAHWARKKVTTQLTGQQLQPSDGVSTQHSDGGKGGWMQRKHPCSFTVCAYNEFARFMATEYQCIHNTIGYTVQPCPKFHDNVYVVVILWKQAKLRYCAYMYRIHAFGQKRELQYHKAVPLTMVHQTSSRPVAGKRYVNFLIKFEYRNRASYTARRRRNCPMSFIQCTPHEEPTYECRVCRWT
19	NIFGNTWKPVDIKPSVTKNAHWADKKCNEQNSEYQLQPSDWVSTQHRDGRGYGWMQQAHPFNFTCCAYNEFKRFMAHETQCIENTIGYTPSRCKKFYDSVGVVKIEKTQHKLEYIALFTRGHAFGQKRETQAHGAVALTMMHQCSVRQVWGKRDPNFYICKEYRNRASYTWRRWRNCYFHNWNCTMHNAPTYNCRVCRWT
P	NIFHNTWKPVDPKPSVTKNEMYIDKKCNEQNSEYQPQPSDWVPTQHRDGCTYGEMQQAHPFWFTCCAYNEFKRFMAFSTICIFNTILDTHKRCKKFEDSVGVLKIEKTQHKLEYIALFTRGHPHGQKRETQAHGAGALTMMHQCWVRQVNGVREENFYIQKEYRNRASYDWRRWRNCRFHNWNCTMHLAPTYNERVCRNT
Q	NIFGNTWKYVDIWPSVTKNASWALIKCAEQNTEYQLNPSDWVVTQHRDGRGYGWAQQAHPFNFTCCAYNCFKRFMWHETQCIENTIGVTPSRCKKFYDSVGCVKIEATQHILEYIALGTRGHAFGQKRETQAHGAVALTMMHDCSVAQVWGKRRPNFYICKEYRWRASYTWRRWRNCKFHNWQCTMHNAPTYNCRVCRWQ
W	NDKGEKSKYEMYTTCVGHLAYPPRKVDTTSNSDSGAFCAADDTGQLRPGRLGGWMQRIHRINITVSWALELARLVADTDVWITFSKGAENNAAHDFFWSIIVVPILMVLPAEFDIVLFTKGKLKLNLRELLFLGAQADDWLHQSDSRIFAGKVRHKFLIHKEYPRLAQYADRIVANNVMTFYAPASPEELVEVKLEMSPT

#NEXUS
[
Generated by seq-gen Version 1.3.2x

Simulations of 10 taxa, 200 amino acids
  for 1 tree(s) with 1 dataset(s) per tree

Branch lengths of trees multiplied by 4

Rate homogeneity of sites.
Model = GENERAL: General time reversible (amino acids)
]

 18 200
11	TEVRSGGGKLSLFALCACFHDIAKSQGGVVRLGEVTDAPHPGGEVLKDEIADGMMDSLQSTVKYDSSYAIAGFTEFNKYNSRNIHDPRTVTEPELLSLPVERLAVFKKVQLLIKGDPWCTRQLAERKYITVLALLGTLKASQHIGYDVKWGSESIINAAIPAENMPNENNQAEDRRLSVHTMAIDLKQFVFRMTRYFQIP
12	TCWRSGQGTLSLFALCACFHDGAKSYGGWVRLGEVTDAPHPGGEVLKDEIWDGMMDSLQSTVKADSSYAYAGCTEFIKVNSRIIHQPFTGTEPELLIKPVERLAVLKRVQLLIKGDPWCTRILAECKYITVLALAITLKASQHIGYDKKWGSEEIINAAIPAENMPNENNVAEDRTLSVVYMATDLVQFVFRMIEYFQIP
13	SCWRSGQGTLSVFALIWCFHDGAKSYGGWVRLCEVTDAPPPGGEVPKCEIWFGMMDCLHSWVKCLSSYAYAGCTEFIKVNSRIIHVFFTGTEPELLHKPIERLAHLKRVQLLIKGDPGCTRIDAENYYITHLALAITIKLVQYIGYVSLWGIEELINAAPPLFNMPNENNFAEDHTLSMVYMAKDLTHFVFFMIEYKQIP
C	SCWRKGQGTLSVFMPIWCFTDGAKSKGPWVHLCGVTDANPWGGEAPKCEIDFGMMDCLHSWVKCLSSYAYAGCTMRIPVNSRIIAPFFTGTEPELLRPPIERLKHLKRAQLLIKGDPWCHVIDAENYYFWHLALAITIKLVQYIGGVSGWGNTCLINKAPPLFNMANHNNFAHDHHLSMVYNAKDLTHFVFSMIEYKQII
D	SCWRSGQGTLSVFALIWCFHDGAKSYGGLVRLCEVMDAPPWKGHVPKCEIWFLMMDPRHSWVFKLSSYAYAGCTEFIHGNSRIIHVFFTGTEPELLHKPIERLAHLKRVQLLIRGNRGATTIDAEQYYICHLALAITVCCVQYIGYVSLWGYEELINAAWPLFNMPNESNFAQDHTLMMVYMAKDYIHFVFFMIEYKQIP
14	TCWRSGQGTLSQFALCACFHDGACSYWGWVRLGSVTIAWHPGGHVLYDEIWDGMMISLQSCVKADSSYAYASCTEMIKFNYAIIHQPFDWCEPELLIKPNERFAELKRVRYLHKEDPWCTRILAECKYTTVKALAITHKAQQHTGYDKKWGSEEIINAAIPAENKPNENNVAEDMTLSVVYQATDLVLFVFRMWEYFQRP
F	TCWPSGQGTLSQFAVCACSDDGACSYWGWVALLKVTIAWHLGGHVLYDEIWDGMFISRQSCVEVDSSYAYANCTEMIKINYAIIHQPFDWCEPELLIKTNQIFFELIRVRYLHKEDMWCERIWAWCKYTTKHALVITHKAHQHTTYKKFWQSEEIINAAIPIENEPNENMVAEDSRLSVVYQATDNVPSVFKMWEYFQRP
15	TCWGSGQGTLSQFYLCCFFHSGACSYWGHVRLGSVTIAMYKGGHVLYDGIWDGMMISLQSCVKADSSYALISCTERIKMNYALIHSPFDWCEPEILIKYNKRFAELYRVRYLHKEDPWCTRILAECKCTEVKALAITHKAQQHTVYDKKWGSEELVNADIKAENKLNENSVAQDFTMSVVYQAADLRLFVFRMWEYFQRP
16	TRWGSGQWTLSCFYLCCFHHKGCFSYWGGVFLGSVTIAMYKGGHVLYKGKIDGMTGSLQSCSKADSSYAAISCTETIKMNYALIHGPFDCCEPELLLKYHKRFAEMQRVRYLHKTDPVMTRILAICECTEVKALAITHQAQQHSVYDKKWGSEELVNADEKAENKLNENDVAQDFTMTVVYIAADLRLFVFRMWEYFMRP
I	VLWGSGQWTWSCFYLCCYYHKGCFSYYGGVFKGSVWIAMYKLGHAFYKGFIDDMTCSLQSCSKADSSYQAIKCMECAKINYALIHGPRDCCEPELLLKYNKRFAENQRVRYLHKTDPYMHGIYKICEVTTMKALAITHQASQHSVYFKKWGSEHLVNAWMQAEYKLNENDVAVDCTMTMVYIAAILVNFVFRMWGYFGWD
17	TRIGSEQWTLSCFYLWCFHHKGCFSYWGGVFLGSVIIAMYKGGHVLYKGKIDSATGMLQSCHKVDMAYADISVTLTIKENYASIHPVFDCCEPEKLAKCHKRFAEMQRVVYLHKTDQVMTRFLAICEITEVKALAITHQASQHSVYDKKQGSEELLNADEKAETKLNENDVAMDFIMTVVYIAADLMLFVFRMWEYFMGR
M	TRIGSSQWFLDCFYLWCFHHKFCFEYYGGVFLGSVIIAMAKGGWTLYKGKIDSATGMLQSCHKFGMAYADISVTLTWKEFYASGHPVFDLCEPEKLAKCHKRQAEMQVVVLLHKTDQVMCRFIAICEHTEVPALAVTHQASQHEVYDKNQGSEELLIADEKLETKLNENDVAMDFIMTVQYIAADLMIFVFRMWEYHMQR
N	RRIGSHEWTLSLQQLWLFHGNGCFSYWGGKFLTSHIIAMYKGGHVLYKGPIDSANGMLQSCHKNDMMYHDISVTLTSKHGYASILKYFDCDGDEKQARCHKIFPEMQRRVYLHKFDQVMTRFLAICEITEFKSLEITHQASQHDVYDKKQGSEELLDAQEKAETKLNENDVAMDFIMTVVYIAADLHLFVMRMWEYFMGR
18	SCWGSGQGTLSQRYLCCFFHLGAMSYWGCVRYGSVTIAMYKGGHDLYAGIWDGMMISLQSCVKADSSQCLMSCTERIKMNWALIHSPFRWCEPEAMHKLNKRFAELPRWRYLHKEDPWCTGILAECKHTEVKALAITHKAQQHTVNDKKWGSEELRNADIKAENKLNENEVAQDFNMSPVAQAADLRLHVFRPWEYFQRP
K	SCWGAPQGGLLQTYLCCFFHLGAMEYWGCHRYGSVTIAMYKGGHDLYAGIWDTMMISLQSCVKATSSQCLMHCTERWTMNEALIHSPFRWCEPEAMHKLNKRRAELPRWRYMVKGDPWCMGILKECKHTHVWALAITHKAHQHQGNTKKWGSEELRNANIKAENKSNENSVAGDFNMSPVAQAADLRLQVFRPWEYFQRP
19	SCWYSGQGWLNLRYLCIFFHLHAMVYPGCKRYGSVPIHLCKGGHILSAGIWCGMMQSLQDKVWAQSSQCLMSCTERIIMIWPDIHDPFRWWEPMAMHKLNKRFAELPRWRYDHKFDPWTTFILAICKNTGQKDLAITHKAQPHTVNDKKWGSEELRNAPITLENKLNENEVANNFNKSPVAHTADLREHDFRPWEYEQRP
P	SHWYSGQGWSNLRYLCIFFHLHAMAIPGKKRYVKVPLHLCKGCHILSAGIWCGMMHSLQNKVWANSSQCLMSCTELIIMIWPDILDPFRWWEPMAMHKTNKRNAELPPWRLDTKFDPWTFFFLAICKNTCQKDPNITHTFQFHTVEDKANGSEGLRNEPITLENKLNCNDEANNFNVSPVAHTADLRTHDFRPWEYEQRM
Q	PRWVSKQGWLNLRYLCFFFHLHAMKYWGCKYYGSVPIHLCKGGHMLLAGIWCLMMQSLQDGAWAQSSQCLMSCTERIVMIWPDAEDPFRWSEPMAMHKLTKRFAPLPRWRVDHKFDPWTTFMLAICKKTGQLDLAIPVKVVPHTYNDKKWGSEWLRNAPITLENKLNENEVPMNFNKSPVAHTKDLAEHDFRQWEYEQRP
W	TEVRAGGGKLSLIALCATFHDIAWSQGGVWILGEVTKAPHPKGDVLKDRIAWMMMDWLQSTVKYDSSYAIAGFTEFNKYNSKNIHDVRTVTEPELLSLPNERLAVFKKVQLWIKGDPWCRRQLAERENITNHALYGTLKASQHNGVDVKWGSESIINAAIPAENMPNENNQAEDHRLSVHGLANCLKQFVFRMTRYFAIP

#NEXUS
[
Generated by seq-gen Version 1.3.2x

Simulations of 10 taxa, 400 amino acids
  for 1 tree(s) with 1 dataset(s) per tree

Branch lengths of trees multiplied by 4

Rate homogeneity of sites.
Model = GENERAL: General time reversible (amino acids)
]

 18 400
11	NQFGNTSKDEDNKAVVGANAYMARKVVTTQNSEPGLQPAAGVSTQHRDGRVGGWDQRIHPFNITVQSYLELARFMAHETECIEESIGYTPNRCKVFKDSDGVVKILWKIAALFYIALFTRGKAFGQKRELLAHKANALTMMHQHSSRQVAGKRDHKFLIKKEYRRRASYTDRRWPNCVMHFGRCTMHEEPWYNKMVCRPTTCWGSGQGTLSQFYLCCFFHSGACSYWGHVRLGSVTIAMYKGGHVLYDGIWDGMMISLQSCVKADSSYALISCTERIKMNYALIHSPFDWCEPEILIKYNKRFAELYRVRYLHKEDPWCTRILAECKCTEVKALAITHKAQQHTVYDKKWGSEELVNADIKAENKLNENSVAQDFTMSVVYQAADLRLFVFRMWEYFQRP
12	NQFGPLSKDEFYKAVVGANAYMARKVVTTQNSEVPLQPAAGVSTQHRIGRQDGLEQRIIPFNITVQSYLELARFMAHETECIELVIGYTPNRFKVFKDTDYVKGELWYIAALFYIALQTRGKAFGQVPWLLAHKANCLTMMHYHSSNQVAGKRDHKTPIKKEYRRRASYTDRRWPNCVMDCGQCQMHEEMKYNFHVCRPTECWGSGQGRLSQFYLCCFFHSGACSYWGHVRLGSVPIAMYKIGPVLYDGPIDGMMISLGTCTKADSSYILLSCHERIKMNYQVINSMIDWCEPEILYKLNKRFAELYRVRYLHAEFPWQYRILAEKKKTEVKALAITHKATQPTVYDKKWESEELVNADIKAENDWNENFVAQDFTMSVVYQAFDLRLYVFRMYPYFQCM
13	VQFKPLSKDEFYKAVVMATAYMARKVVTTQNSEVPTQPAAGVTTQHRTGRKDGGEPRIIPFNMTVQSYLHYARPRAFLTECIQNDIGYRPNRFKSFCMTDYVKGMLRYRAALFRIALQTRGKAFGYPPWLLAHKANCLTFMHYHSSNQVAGTRDRKTPIKKRYRRAASYIDRGWPNCKQDCMQCQMHEEMSYNFHVCRPTWCVGSKFGRLSSFYLNCFFHSGACSYWGHVRLGSVKIHMYKIGPVLYDGPIDGMMISLGTCTAIDLSYIVCSCHERIKMNYQVINTMWDWCEPEKLYKLNKRFAELYRVRDLHATFPWQYREPAEIKKTNVKALAETHKATQPTVKDLKWESEELMNFDIKAENDPNENFVAQDFTMSEKYQAFDSRWMVFVMYPYFQCM
C	VQFKPLSKDEFYGAVSMATAYDARKVVTDQHDEVYIQPAAGVTTQHRTGRKDGGEPRIIPFNVTVASYLHYAMPRAFLTECIQNDIGYRHMVFKSFCMMDNVKQVLRYRAALIRIALQTMGKAFGIGPWLLAHKANCLTFMYYHVSNQVAFTRIRKTPITKCYRNIASYIDRDWPNCKMDVSQCQMHEAMSYNFHVCRPTWCVGSKFGTLSSFYLNCFFHSGDCSYWGHRRLGSVTIGMYKIGPLLYDRPIDGMMISFGTCTAIDLWYIVCHCHEFIKMNYQEACTMWDKCEPESLYKLNKRFAELYRVRDFHATFPWQYREPTEIKKTEVKALAETIKATQPTHKDLKYGSEELMNPDINAENDPNENFVAQTFTMSEKYQCIDSRWMVFVMYPDFQCM
D	VQFKPLSKDQFYKAVVMATAYMNRKVVTTQLQEVPTPPAHGVTTQHRSGRKRGGEPRISPFNMKVQKNLHYARPRAFLKECIQNDMGIRYNRFKSFCMTDYVKGMPRWRRAEFCIGHGTKDKAFGYPPWLLLHLANCLTNMHYSSFNRVATTRDRKTPIDKRPRRASSYEYRGFAACKQDCMQCQMHEEMSYNFHVRRYDWEVPSQFDRLSTFYLLCFFHSGACGGWGHVRWGSVKIHMCKIGPVLYDGPIAGMMISLGGCTAQDLSYIVCSCHDRIKMNYMVDNTMWDWCEPEILYKLNYKFAELYRVRDLHATFPWCYRAMAEIKKTNVKALAETHYATQPTVKDPKWESEEGYNFDIKYENFMNENEVIQDFTMYEKYQAFDSRWMVFVMYPYEGCM
14	NVFGPLSKDSFYMMVVGANAAMAIKVVTTQNSEQPLQPAAGVSTQHRIGDQDGLEQRIIPFNIPVQSYLRTARFTAHEQECIELVIGLTPNRFKVFKDTDYVKGILWYIAALFYIALQTYGKVFSEFPALLRHKANCLTMSKYHSSNQSAGKRDIATPIKKEYGRRASYTDRRWPNCVMDCLQCQMKEEMKYVFHVCRPTECWGSGQGRLSQCYLCCFFWSGFCSYWEHVRLGSVPIAMTKIGPDHYDGKDDGMMIQLGTCTKADSMYILLFCHERITHKYQVGNSMIDWCIPEILYKLIKRFAELYRVRNLHAEFFPQYRIFAEKKKTERKALNITYKWEQPTVYEKKMESEELTQLDIKAENDWNEFFMAQAGTTSVTYQALDLRLYVFRMYPYFHCM
F	NDFGPLSKDSFHMMVVGMNAAMYIKVVTTQNSEQPIQPVAGVSTNHMIGDYSGCTQHIIPFSTPVQSYLVVARFLPHRQECFEPPIGLTPNRFWVFKDTYYVKGILWIIGALFYIAPQTYGKWFSEFLALVRHKANCLDGSKYHSSNQSAPKPDIATPIFKEGQRRASYLRTDWGGCVMDCLQCQMIREMKYVFFVCRPTECWGSGQGRLSQCYLCCFFWSGFCGYWEHVRLGSVWIAKTTRGPDVADHKDIGMMIQLGTCDGADSMYILWFCHERITHKYQVGNEMIDRCIPEILWRLYKRFAELYRRRNMHAEFFPYYLIFAEKKKTERKALNITCRWEQPTRYCKFPESPELTQLPIKAECDWNEFFMAQAGTTSVTYQAWDVRLYQLRMYPYFHCM
15	NVFGALSKCSFYIYVVGANCAMAIKVVTTQNSEQPGQPAAGVSTQHRISDQDGLECQPIPFNIPVQFYLRTAQFTAHEQQCIEMVIGLTGNRFKVFKDTDYVKGINWYIVALFIINLQTYGKVFSEFPALLRHKARCDTVSKYHSSNLSADPFDIFTSIKKEYGRRASYMERRWPNCQMWPLDCQMKVETGYVFHVCRPTECWGSGFGSLSQCYLYCFFWSGFCSYWGHVRLGSVPIALGKIGPDHYDGKDDGMMIQQGTCTKADSMYILYFCHDRIKHKLSVGNSMPDWCISEILYKLIKRFAELYRQRNPVAELWPQYGVFAWKKKTERKALNITYKWEPPTVYPKKMEKEELTQLDVKDENDWKEFFMAQAGTGHVTYQNEDLRLYITRMYPYFDCS
16	NVFGALFKCSFYIYVIGANCAMVIPLVTTYNSWQPGQLAALVSTQHRISDQDGLECFPIMFLIPVTFYLRTAQFTAHIQQCIEMVIGLTGNRFKSFCDTDYVPAINWYIVALFSINLQTYLKQFSEFPALLRRKARCDTVSKYHSSDLSADPFWIFTSIKKEYERRASYWERRWPNFQMWPLFEQMKVETDKHFHVCRPTECWGSFFLSLSQCYLYCFFWSGGCSIMDRVRLGYVPIANGKIGDDSYDGKDDGMMYQQKTIYKADVMYHLYFSHDRIEHKLSVGNVMPDWCIYDIVYKLIKRFAELYRQIAPHAILWPKYGVFAWKKKTERKGLNITCKWEPEDVYPKKYEKEHLSQKDFKDENSWKTFFMAQAGTGCVTYQNEDLRLYITRMYHYFDCS
I	NVFGALFKCSYYHMYVGANKAMVIPRVDTYGSWQRGQLAALVSTQHRISWQDGWECFPIMELSPVTFYPRTAFFTAHIQQTINMVEGLTCYCAKSFCDTFDVVAINMYSVALFSDCLQPYLKQCSEFPALLRCQARCCYVSKYHSSDLSSDPKWIFTGIKKEDERRACYWEKRWPNFQMWLLFLQMLVETDKHFHDCRPCECWGGFFMILSVCYPNFFFWNGACSIMDRHRKGYVPIAEPKHGDDPYDDKDDWMMYQAKHICKADVMYHLYFSHDRIEHDLSVGNYYPDWWIYSIVYKLGREFAELCRQPRPHTIAWPKTGLHGWVKKTERKGLEITCKTEPEDVYPKKYCKEHLSQKDCKDENSRKTFYMAQYGTGCQTYQNEDLRLYITRDYHYHDSS
17	NQFLAYFKCSFYFYWTGAGCFMMFILHDTYNSWQPGQLAALVSTQERIPDQDGCECFKIMFLIPVTFYVRTAQFTLGIQQCIEMVIGLTGNTFISFCDTDYVPCIECYIVALFSINLTTYLKQFSEFPALLRRKHLCDTQLVYHSSDLSADPFWIFTSIKQEYERRASYWESRWPNFQMWLLEEQMHVETTKHFHKCVPVECWGSFFLFLSQCYLYCFFWSGGCSEMDRVRLGCVPIANIKIGQDSYDGKNDGSMYQQKTIYKAVVMYHLHFSHDRIETKLSVGNVNPDWCIYDYVYKLIKAFAELYEQHAPHAILWPKYGVFAWWKKTERKHLNITYQWLPEDVYPKKYEKEHLWQKEFKDENSWKTFYMAFAGTGCVTYPNEKWLLVITRMRFFFACS
M	NQFLWYFKCSLYQYIRGAGCFMMFILHWTYNSWQPGQGACLQSMQEDIPDQDFCNIFKIKFLLMVCFYVFTAQFTLGIQQCIEEVIGLTGNTFIMFCDTDYQPCIYCYIVALFSINITTKVKQFSVFCALDRRYHLCDTQPVMHSSVLSADPFWIFTSIKQEYERRAEYHECRWPNRQMWLSEEKMHVHTTKHFHKCVPVECWGSFFQFLSQCYLYCFFWSGGCFEYDRVRWGCVPIANIYIGQDSYSGNNDGSMYQMYDMYKAYVLYHLHFSHDRIETKLSQGLVNPWQCIRDYVYKLPKAFAELYEQHAPHSILWPKYGVFALWKKTERKHQNITYQWLEEDVYPKRYEKEHGWQKEFEDENSWKTFYMSFAGTGEVTYPNEKWLTVIYRMRFFFACS
N	NQSLAYFKCFFYFYWTGIGCFMRFILHDTYTSWQPGQLAALVSTQVRGPDQDGCEKFKIMFLIVVTFMYRCAQRGLEIQHPIEMVIKMTGNTFISEFATTYVPCIECYIVALRSINLTTSLKQCSEFPALLRRWHLCDTQLVYHLSDLSADHFWIFTSIKTEYERRALYWESLWPRFNMWLLEEQMHVETTKHFHNCVNVECWGSFFLFLIQCILYCFFKMGGCSEMDRVMLGCVPIANSEIDQDSYDGKNDGSMYQQKTILKAVCMYDLHFSHDRGECKLQAHEVNPDWCIPDWVYKLINKFAELLEVHAPAAKLWPKFGVFAWWKFRERNHLNVTQQWLPEDVYPHKAVKEGLWQKELEDENSWKTFYMAFLGTGCVTYNNEKWLLYGTRYWFHFACS
18	NVFGALRKCSFYIVVVGANAAMAIKKVTTTNSEQPGQLAAGVSTHHDISDQDGLYCQPIPFNIPVQFYMRTAQETAHEQQCGEMVIGLTGNRFKVFKDTDYVKGIAWYIQALFIINLQTYGKRFSEFPALSRHKARFDTSSKYISSELSMDPFDFFTSWKKEYGRIASYMQRRWPNYSMWPLDCQMKVETGYVFHVCRPTECWVSGFTSYSQCYLYCLFWSGFCSKWGHVLLPLVVIILGKIGPDHYDGKDDLMMIQQWTCNKADSMYILYFCHDRINHKLSVGISMPDWDISEILYKWIKVFAELYRQRNSVAELWPQYGIFSWKKREEPKKLNITYKWEPPTFYPKKMEKEELTWLCVKDENDWDEQTMALALTGHVTYQNEDLRLYMTRMYPYFDCQ
K	NVFGALRKCSSHDVVVGARAAMAIKKVTTTKSLQPGQLAAGVSEHHDISDQQCLYCQPIPFNIPVQFYNRTASEDADLQQQGEMSIGLTGNRFKVFKDTDYVEIIAWYIQALFIISLQTWRKRFSEFPALSRHKARFDTSSKYESSELSMWPKDFFTSWKKEYGRIAIYMQRRWPNYLMWPADCLMKVEDGYQFHVFRPTEGWVAEPTSACQCQLYCLFWSLFCRKWGHVLLPLFVIILGRIGPDHYDGKDDLMMIQQWTCNKADSMYISYQCHDRINHKHSIGISMPDWKISEELYKWIKVFIELYRQRNSVAELWPQYGIFQWKKFEEPNLLNITYKWEPPTNMPKKMEKEEQVWLCVKDENDWAEQTMANAHTEHVTYWCADLRLYMTRMYPYADCQ
19	NVFGALRYCSFYIVVVGASAAMAIKKVTTTNYEQPGQCAAGVSTYHDISMQDGLYCQNIPFCIPNQIYMRTAYEAAHEQQCFQMVIGLTGNRFKVWKNTWYVKGIAWYPQALFHINLQLYGKTKSQFWADSRQKARFDTSSKYISSNLSMDPFDPFDSWKKEYGRIASYMLRRWPNYSMWPLDCQMKVWTGHVFHVCRPTECWVSGFTSYSQEYLYQFFWSGFCSSWGHVLLPLVVIIQGKIGPDHYIGKDCMESVQQWTCNKAGGMYFGPFCHDAISHKRSDGVSCPDRDISEILTKWIKVFAHLYIQRNWVAGLWPQYGIFSWKKRWEPKKGHITYKWEPPTFYPAKEDKPELTPLCVKDENDWHEQTLFLAIMGHVTYQNETLRLYMTRSYPYMECQ
P	KEFKALRYCSFYISVVGASATMAIKKVTTTNYAQPGQCAAGVSTYHDILMFDGLYNQNIPHCIPNQIYGRTPYEAAHEQWGDQMVIGLTLNGFKVWKNTWYVKGRCWYPMYLFHINAQLYGKTHSQFWRDSWDYTRFTTSSKYIFSNWSMDPFFPFDSWKKEFGRIASYMLRRWDIYSMWPLDCQMKVWTHHVFNVCRPTECWVSGFTSYSQEYLYQFFWSWFCSIWGHVLLELVVIIQGKIGPDHYIGKDCMESVQQWTCRRAGGSYFGPFCHDAISHKRSQGVSCPDPQIWRILTKTIKVFARRWIQRNWVAGKWPQYGIFGWKKYKEPKKGHITYKWEPRTFYPAKEGKPLLCPLFVKDEADLHEQTLFFSYMGHQHYQNYRFRLYMFRRYPYMECQ
Q	NPFGAERYTSFYIVVVGASAAMAIKKVTENDYEQFGQCAGGVSTYHDISMQDGLYVQNIPFCIPNQQYMRTAYEAQHVQQCFQMVIGLTTNAFKVWKNTWYVKGIEWRPQGLFHANFQLYGWTKSQFWADKRQKARFDTSSIYIVSNLSNNPFDPFDSWKKPYGRQGSYMLRRHPLESKWPPDCQMKVWTGHVFNVARFQECWVSGFTSYSQEYLYQFFWSGFCSSWGHVLLNLVVIIQGKIGPDHYIPKDCMQSVQQWRKNFAGGMLFKPFCHDAISHKYSDGVSCPDRDIREISTKWIKAFAHLYIQRKWVAGLWPQYGIFSWKKRWEPKKMMITYSQEPPTFYPNKEWFVEYMKLCVADENDWIEQALFLAIMGHVTYQNNTLRLYMTRSYPYMFCQ
W	NQFYNTSKDEDNKMVVGANPYMARKVVTPQQSWGGLQPAAGVSTQHWDGRYGCQSQRIHWFNITVQSALELARFMAVETECIRESRGYTPHRGKVFKDVDGVVGQFWKIAALFYIALFTRGKAFGQQRELLAHKANVLTMMHWHSSFQVAGRRDIKFGIKKECRRRASYMDHRWPNIVMHQGKCTMHEEPWYNRMVCRPTTCHGSGDGTLSQFYGCCFFHSGACSYWGHVWLGSVVIAMGKGGHSLYDGIQDGMMISLYSWVKPFSSIALISCTERWHMNYAIIHSPFDWCWPGILILYNKRFAELYRVRYLHKECFVCTFILAECACTEVKAGWITHKAQMHTVYDKKWGSEGLVNADIHAEDKLNENSVIQDFTMSVVYQAADLRLFVFMMWEYFQRL
```