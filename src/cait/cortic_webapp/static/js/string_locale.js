/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, May 2020
  
 */

'use strict';

var locale="en/CA";

var localizedStrings={
    login:{
        'en/CA':"User Login",
        'fr/CA':"Utilisateur en ligne",
        'chs/CN':"用户登录"
    },
    username:{
        'en/CA':"Username",
        'fr/CA':"Nom d'utilisateur",
        'chs/CN':"用户名"
    },
    usernameReq:{
        'en/CA':"Username is required",
        'fr/CA':"Nom d'utilisateur est nécessaire",
        'chs/CN':"用户名为必填项"
    },
    pass:{
        'en/CA':"Password",
        'fr/CA':"Mot de passe",
        'chs/CN':"密码"
    },
    passReq:{
        'en/CA':"Password is required",
        'fr/CA':"Mot de passe requis",
        'chs/CN':"密码是必需的"
    },
    loginBtn:{
        'en/CA':"Login",
        'fr/CA':"S'identifier",
        'chs/CN':"登录"
    },
    usernameNotExist:{
        'en/CA':"Username does not exist!",
        'fr/CA':"Le nom d'utilisateur n'existe pas!",
        'chs/CN':"用户名不存在！"
    },
    usernameExist:{
        'en/CA':"Username already exists!",
        'fr/CA':"Ce nom d'utilisateur existe déjà!",
        'chs/CN':"此用户名已存在！"
    },
    wrongPass:{
        'en/CA':"Incorrect password!",
        'fr/CA':"Mauvais mot de passe!",
        'chs/CN':"密码错误！"
    },
    usernameOrPassEmpty:{
        'en/CA':"Username or password cannot be empty!",
        'fr/CA':"Le nom d'utilisateur ou le mot de passe ne peuvent pas être vides!",
        'chs/CN':"用户名或密码不能为空！"
    },
    initCAIT:{
        'en/CA':"Starting CAIT System",
        'fr/CA':"Démarrage du système CAIT",
        'chs/CN':"正在启动CAIT系统中"
    },
    createAcc:{
        'en/CA':"Create your Account",
        'fr/CA':"Créez votre compte",
        'chs/CN':"创建您的帐户"
    },
    signupTitle:{
        'en/CA':"Signup to start using CAIT",
        'fr/CA':"nscrivez-vous pour commencer à utiliser CAIT",
        'chs/CN':"注册以开始使用CAIT"
    },
    register:{
        'en/CA':"Register",
        'fr/CA':"S'inscrire",
        'chs/CN':"注册"
    },
    cancel:{
        'en/CA':"Cancel",
        'fr/CA':"Annuler",
        'chs/CN':'取消'
    },
    registerSuccess:{
        'en/CA':"Registration succeeded!",
        'fr/CA':"Inscription réussie!",
        'chs/CN':"注册成功！"
    },
    vpTitle:{
        'en/CA':"Cortic A.I. Toolkit",
        'fr/CA':"Cortic A.I. Boîte à outils",
        'chs/CN':"Cortic A.I. 工具包"
    },
    loggedInAs:{
        'en/CA':"Logged in as: ",
        'fr/CA':"Connecté en tant que: ",
        'chs/CN':"登入为: "
    },
    save:{
        'en/CA':"Save",
        'fr/CA':"Enregistrer",
        'chs/CN':"保存"
    },
    saveName:{
        'en/CA':"Filename to save: ",
        'fr/CA':"Nom de fichier à enregistrer: ",
        'chs/CN':"要保存的文件名： "
    },
    new:{
        'en/CA':"New",
        'fr/CA':"Nouvelle",
        'chs/CN':"新工作空间"
    },
    saveOrNot:{
        'en/CA':"Do you want to save your current workspace?",
        'fr/CA':"Voulez-vous enregistrer votre espace de travail actuel?",
        'chs/CN':"您要保存当前的工作空间吗？"
    },
    load:{
        'en/CA':"Load",
        'fr/CA':"Charger",
        'chs/CN':"加载"
    },
    loadName:{
        'en/CA':"Filename to load: ",
        'fr/CA':"Nom de fichier à charger: ",
        'chs/CN':"要加载的文件名： "
    },
    run:{
        'en/CA':"Run",
        'fr/CA':"Exécutez",
        'chs/CN':"运行"
    },
    stop:{
        'en/CA':"Stop",
        'fr/CA':"Arrêtez",
        'chs/CN':"停止"
    },
    genPython:{
        'en/CA':"Generate Python Code",
        'fr/CA':"Générer du code Python",
        'chs/CN':"生成Python代码"
    },
    genPyName:{
        'en/CA':"Filename to save generated python code: ",
        'fr/CA':"Nom de fichier pour enregistrer le code python généré: ",
        'chs/CN':"保存生成的python代码的文件名： "
    },
    genPyNB:{
        'en/CA':"Generate Jupyter Notebook",
        'fr/CA':"Générer le bloc-notes Jupyter",
        'chs/CN':"生成Jupyter笔记本"
    },
    genPyNBName:{
        'en/CA':"Filename to save generated jupyter notebook: ",
        'fr/CA':"Nom de fichier pour enregistrer le notebook jupyter généré: ",
        'chs/CN':"保存生成的jupyter笔记本的文件名： "
    },
    visInit:{
        'en/CA':"Initializing vision module...",
        'fr/CA':"Initialisation du module de vision ...",
        'chs/CN':"初始化视觉模块..."
    },
    voiceInit:{
        'en/CA':"Initializing voice module...",
        'fr/CA':"Initialisation du module vocal ...",
        'chs/CN':"初始化语音模块..."
    },
    nlpInit:{
        'en/CA':"Initializing nlp module...",
        'fr/CA':"Initialisation du module nlp ...",
        'chs/CN':"初始化自然语言处理模块..."
    },
    controlInit:{
        'en/CA':"Initializing control module...",
        'fr/CA':"Initialisation du module de commande ...",
        'chs/CN':"初始化控制模块..."
    },
    sHomeInit:{
        'en/CA':"Initializing smart home module...",
        'fr/CA':"Initialisation du module maison intelligente ...",
        'chs/CN':"初始化智能家居模块..."
    },
    visNotInit:{
        'en/CA':"Vision is not initialized. Please initialize it in the setup block first.",
        'fr/CA':"La vision n'est pas initialisée. Veuillez d'abord l'initialiser dans le bloc de configuration.",
        'chs/CN':"视觉未初始化。请首先在设置块中对其进行初始化。"
    },
    voiceNotInit:{
        'en/CA':"Speech is not initialized. Please initialize it in the setup block first.",
        'fr/CA':"La parole n'est pas initialisée. Veuillez d'abord l'initialiser dans le bloc de configuration.",
        'chs/CN':"语音未初始化。请首先在设置块中对其进行初始化。"
    },
    nlpNotInit:{
        'en/CA':"NLP is not initialized. Please initialize it in the setup block first.",
        'fr/CA':"NLP n'est pas initialisé. Veuillez d'abord l'initialiser dans le bloc de configuration.",
        'chs/CN':"自然语言处理未初始化。请首先在设置块中对其进行初始化。"
    },
    controlNotInit:{
        'en/CA':"Control is not initialized. Please initialize it in the setup block first.",
        'fr/CA':"Le contrôle n'est pas initialisé. Veuillez d'abord l'initialiser dans le bloc de configuration.",
        'chs/CN':"控制系统未初始化。请首先在设置块中对其进行初始化。"
    },
    sHomeNotInit:{
        'en/CA':"Smart Home Control is not initialized. Please initialize it in the setup block first.",
        'fr/CA':"Smart Home Control n'est pas initialisé. Veuillez d'abord l'initialiser dans le bloc de configuration.",
        'chs/CN':"智能家居控制未初始化。请首先在设置块中对其进行初始化。"
    },
    logout:{
        'en/CA':"Logout",
        'fr/CA':"Se déconnecter",
        'chs/CN':"登出"
    },
    setupWelcome:{
        'en/CA':"Welcome to the CAIT setup",
        'fr/CA':"Bienvenue dans la configuration CAIT",
        'chs/CN':"欢迎来到CAIT的设置页面"
    },
    lastUpdate:{
        'en/CA':"Last updated: May 22, 2020",
        'fr/CA':"Dernière mise à jour: 22 mai 2020",
        'chs/CN':"上次更新时间：2020年5月22日"
    },
    connectWifi:{
        'en/CA':"Connecting to WiFi network",
        'fr/CA':"Connexion au réseau WiFi",
        'chs/CN':"让我们连接到WiFi网络"
    },
    selectedWifi:{
        'en/CA':"Select WiFi",
        'fr/CA':"Sélectionnez WiFi",
        'chs/CN':"选择WiFi"
    },
    availWifi:{
        'en/CA':"Click for WiFi list",
        'fr/CA':"Cliquez pour la liste WiFi",
        'chs/CN':"可用的WiFi"
    },
    enterPassword:{
        'en/CA':"Enter Password",
        'fr/CA':"Entrer le mot de passe",
        'chs/CN':"输入密码"
    },
    connect:{
        'en/CA':"Connect",
        'fr/CA':"Relier",
        'chs/CN':"连接"
    },
    loadingTextWifi:{
        'en/CA':"Testing WiFi Connection",
        'fr/CA':"Test de la connexion WiFi",
        'chs/CN':"测试WiFi连接"
    },
    loadingReboot:{
        'en/CA':"Cleaning up and rebooting CAIT",
        'fr/CA':"Nettoyage et redémarrage de CAIT",
        'chs/CN':"正在重新启动CAIT中"
    },
    doneTextWifi:{
        'en/CA':"Please refresh this page in a few minutes",
        'fr/CA':"Veuillez actualiser cette page dans quelques minutes",
        'chs/CN':"请在几分钟后刷新此页面"
    },
    wifiSuccess:{
        'en/CA':"WiFi Connection successed! CAIT will reboot now. Please switch to your selected Wifi and wait for a few minutes",
        'fr/CA':"Connexion WiFi réussie! CAIT va redémarrer maintenant. Veuillez basculer vers votre Wi-Fi sélectionné et patienter quelques minutes",
        'chs/CN':"WiFi连接成功！ CAIT现在将重新启动。请切换到您选择的Wifi，然后等待几分钟。"
    },
    wifiFailed:{
        'en/CA':"Cannot connect to selected WiFi, please refresh this page and try again.",
        'fr/CA':"Impossible de se connecter au WiFi sélectionné, veuillez actualiser cette page et réessayer.",
        'chs/CN':"无法连接到所选的WiFi，请刷新此页面，然后重试。"
    },
    startSetup:{
        'en/CA':"Start setup",
        'fr/CA':"Démarrer la configuration",
        'chs/CN':"开始设定"
    },
    customDevice:{
        'en/CA':"Setup your device",
        'fr/CA':"Configurez votre appareil",
        'chs/CN':"自定义您的设备"
    },
    nameDevice:{
        'en/CA':"Hostname",
        'fr/CA':"Nom d'hôte",
        'chs/CN':"您想如何命名您的设备？"
    },
    askUsername:{
        'en/CA':'Username',
        'fr/CA':"Nom d'utilisateur",
        'chs/CN':"您的用户名是什么"
    },
    askPassword:{
        'en/CA':"Password",
        'fr/CA':"Mot de passe",
        'chs/CN':"请输入您的用户密码"
    },
    testHardware:{
        'en/CA':"Peripheral test",
        'fr/CA':"Test périphérique",
        'chs/CN':"我们将测试连接的摄像头和音频设备"
    },
    availCam:{
        'en/CA':"Available Camera(s)",
        'fr/CA':"Caméra(s) disponible(s)",
        'chs/CN':"可用摄像头"
    },
    availAudDevices:{
        'en/CA':"Available Audio Device(s)",
        'fr/CA':"Périphérique (s) audio disponible (s)",
        'chs/CN':"可用的音频设备"
    },
    testCam:{
        'en/CA':"Test Camera",
        'fr/CA':"Caméra de test",
        'chs/CN':"测试摄像头"
    },
    testSpeaker:{
        'en/CA':"Test Speaker",
        'fr/CA':"Test du haut-parleur",
        'chs/CN':"测试扬声器"
    },
    testMicrophone:{
        'en/CA':"Test Microphone",
        'fr/CA':"Microphone de test",
        'chs/CN':"测试麦克风"
    },
    loadingTextHardware:{
        'en/CA':"Initializing Hardware",
        'fr/CA':"Initialisation du matériel",
        'chs/CN':"初始化硬件"
    },
    thirdSignin:{
        'en/CA':"Cloud Service Provider",
        'fr/CA':"Fournisseur de services cloud",
        'chs/CN':"让我们登录或注册到第三方云服务提供商，创建帐户后，请在下面输入API Key和Secret Key，然后按下一步按钮"
    },
    thirdLoginin:{
        'en/CA':"Create Google Service Accont",
        'fr/CA':"Créer un compte de service Google",
        'chs/CN':"让我们登录或注册到第三方云服务提供商"
    },
    thirdsignin_explain:{
        'en/CA':"You may choose to connect to a cloud service provider for better speech recognition/generation performance.  However, if privacy is important to you, you may skip this step and opt to process audio inputs locally.",
        'fr/CA':"Vous pouvez choisir de vous connecter à un fournisseur de services cloud pour de meilleures performances de reconnaissance / génération de la parole. Cependant, si la confidentialité est importante pour vous, vous pouvez ignorer cette étape et choisir de traiter les entrées audio localement.",
        'chs/CN':""
    },
    thirdsignin_upload:{
        'en/CA':"Please refer to the User Manual for a step by step Google setup guide",
        'fr/CA':"Veuillez consulter le manuel de l'utilisateur pour un guide de configuration Google étape par étape",
        'chs/CN':""
    },
    json_upload:{
        'en/CA':"Please upload the JSON file from Google",
        'fr/CA':"Veuillez télécharger le fichier JSON de Google",
        'chs/CN':""
    },
    signinSuccess:{
        'en/CA':"Sign in successful! Please press the Next button to continue.",
        'fr/CA':"Connexion réussie! Veuillez appuyer sur le bouton Suivant pour continuer.",
        'chs/CN':"登录成功！请按下一步按钮继续。"
    },
    next:{
        'en/CA':"Next",
        'fr/CA':"Suivant",
        'chs/CN':"下一步"
    },
    previous:{
        'en/CA':"Previous",
        'fr/CA':"Précédent",
        'chs/CN':"上一步"
    },
    skip:{
        'en/CA':"Skip",
        'fr/CA':"Sauter",
        'chs/CN':"跳过"
    },
    skipWifi:{
        'en/CA':"If you skip setting up the WiFi, you can only connect to CAIT through AP mode",
        'fr/CA':"Si vous ignorez la configuration du WiFi, vous ne pouvez vous connecter à CAIT qu'en mode AP",
        'chs/CN':"如果您跳过设置WiFi，则只能通过AP模式连接到CAIT"
    },
    skipDeviceInfo:{
        'en/CA':"If you skip setting up account, you will not have a personal account for Visual Programming",
        'fr/CA':"Si vous ignorez la configuration du compte, vous n'aurez pas de compte personnel pour la programmation visuelle",
        'chs/CN':"如果您跳过设置帐户，则将没有用于可视化编程的个人帐户"
    },
    skipBaidu:{
        'en/CA':"If you skip setting up Baidu account, you will not be able to use online speech services",
        'fr/CA':"Si vous ignorez la configuration du compte Baidu, vous ne pourrez pas utiliser les services vocaux en ligne",
        'chs/CN':"如果您跳过设置百度帐户的操作，则将无法使用任何云端语音服务"
    },
    thirdlogin:{
        'en/CA':"Login/Register Baidu Account",
        'fr/CA':"Se connecter / S'inscrire au compte Baidu",
        'chs/CN':"登录/注册百度帐号"
    },
    apiKey:{
        'en/CA':"API Key",
        'fr/CA':"Clé API",
        'chs/CN':"API Key"
    },
    secretKey:{
        'en/CA':"Secret Key",
        'fr/CA':"Clef secrète",
        'chs/CN':"Secret Key"
    },
    emptyField:{
        'en/CA':"None of the fields can be empty!",
        'fr/CA':"Aucun des champs ne peut être vide!",
        'chs/CN':"所有字段不能为空！"
    },
    congrats:{
        'en/CA':"Restart Your Device",
        'fr/CA':"Redémarrez votre appareil",
        'chs/CN':"请单击下面的按钮立即重新启动CAIT"
    },
    reboot:{
        'en/CA':"Restart CAIT",
        'fr/CA':"Redémarrez CAIT",
        'chs/CN':"重新启动CAIT"
    }
}
