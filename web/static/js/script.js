let asciiFrames = [];
let asciiIndex = 0;
let asciiInterval = null;
let asciiVelocidadeAtual = 450;

let recognition = null;
let ouvindo = false;

const CONFIG_PADRAO = {
    satelite: "🌙",
    tamanhoGlobo: "8",
    mostrarSatelite: true
};

// =========================
// ⚙️ CONFIGURAÇÕES
// =========================
function carregarConfig() {
    try {
        const salva = localStorage.getItem("jarvis_config");

        if (!salva) {
            return { ...CONFIG_PADRAO };
        }

        return {
            ...CONFIG_PADRAO,
            ...JSON.parse(salva)
        };
    } catch {
        return { ...CONFIG_PADRAO };
    }
}

function salvarConfig(config) {
    localStorage.setItem("jarvis_config", JSON.stringify(config));
}

function aplicarConfig(config) {
    const lua = document.getElementById("lua");
    const globo = document.getElementById("asciiGlobo");

    lua.textContent = config.satelite;
    lua.style.display = config.mostrarSatelite ? "block" : "none";

    globo.style.fontSize = `${config.tamanhoGlobo}px`;
    globo.style.lineHeight = `${config.tamanhoGlobo}px`;
}

function configurarPainelConfig() {
    const configBtn = document.getElementById("configBtn");
    const configPanel = document.getElementById("configPanel");
    const satelliteSelect = document.getElementById("satelliteSelect");
    const globeSizeRange = document.getElementById("globeSizeRange");
    const showSatelliteCheck = document.getElementById("showSatelliteCheck");
    const resetConfigBtn = document.getElementById("resetConfigBtn");

    let config = carregarConfig();

    satelliteSelect.value = config.satelite;
    globeSizeRange.value = config.tamanhoGlobo;
    showSatelliteCheck.checked = config.mostrarSatelite;

    aplicarConfig(config);

    configBtn.addEventListener("click", () => {
        configPanel.classList.toggle("hidden");
    });

    satelliteSelect.addEventListener("change", () => {
        config.satelite = satelliteSelect.value;
        salvarConfig(config);
        aplicarConfig(config);
    });

    globeSizeRange.addEventListener("input", () => {
        config.tamanhoGlobo = globeSizeRange.value;
        salvarConfig(config);
        aplicarConfig(config);
    });

    showSatelliteCheck.addEventListener("change", () => {
        config.mostrarSatelite = showSatelliteCheck.checked;
        salvarConfig(config);
        aplicarConfig(config);
    });

    resetConfigBtn.addEventListener("click", () => {
        config = { ...CONFIG_PADRAO };

        satelliteSelect.value = config.satelite;
        globeSizeRange.value = config.tamanhoGlobo;
        showSatelliteCheck.checked = config.mostrarSatelite;

        salvarConfig(config);
        aplicarConfig(config);
    });
}

// =========================
// 🌍 ASCII GLOBO
// =========================
async function carregarAsciiGlobo() {
    try {
        const resposta = await fetch("/static/ascii/earth_frames.json");
        asciiFrames = await resposta.json();

        if (asciiFrames.length > 0) {
            document.getElementById("asciiGlobo").textContent = asciiFrames[0];
        }
    } catch (erro) {
        document.getElementById("asciiGlobo").textContent = "🌍";
        console.warn("Não consegui carregar earth_frames.json", erro);
    }
}

function iniciarAsciiGlobo(velocidade = 450) {
    const globo = document.getElementById("asciiGlobo");

    if (!asciiFrames.length) return;

    if (asciiInterval && asciiVelocidadeAtual === velocidade) return;

    pararAsciiGlobo();

    asciiVelocidadeAtual = velocidade;

    asciiInterval = setInterval(() => {
        globo.textContent = asciiFrames[asciiIndex % asciiFrames.length];
        asciiIndex++;
    }, velocidade);
}

function pararAsciiGlobo() {
    if (asciiInterval) {
        clearInterval(asciiInterval);
        asciiInterval = null;
    }
}

function estadoIdle() {
    const globo = document.getElementById("asciiGlobo");

    globo.classList.remove("globo-thinking");
    globo.classList.remove("globo-speaking");

    iniciarAsciiGlobo(650);
}

function estadoThinking() {
    const globo = document.getElementById("asciiGlobo");

    globo.classList.add("globo-thinking");
    globo.classList.remove("globo-speaking");

    iniciarAsciiGlobo(180);
}

function estadoFalando() {
    const globo = document.getElementById("asciiGlobo");

    globo.classList.remove("globo-thinking");
    globo.classList.add("globo-speaking");

    iniciarAsciiGlobo(320);
}

// =========================
// 💬 MENSAGENS
// =========================
function mostrarMensagem(autor, texto, tipo) {
    const mensagem = document.getElementById("mensagemAtual");

    mensagem.className = "mensagem-atual";
    mensagem.classList.add(tipo);
    mensagem.classList.add("entrando");

    mensagem.innerText = `${autor}: ${texto}`;
    mensagem.classList.remove("hidden");

    setTimeout(() => {
        mensagem.classList.remove("entrando");
    }, 300);
}

// =========================
// 🔊 TTS
// =========================
function falarTexto(texto) {
    if (!("speechSynthesis" in window)) {
        estadoIdle();
        return;
    }

    window.speechSynthesis.cancel();

    const fala = new SpeechSynthesisUtterance(texto);
    fala.lang = "pt-BR";
    fala.rate = 1;
    fala.pitch = 1;

    fala.onstart = () => estadoFalando();
    fala.onend = () => estadoIdle();
    fala.onerror = () => estadoIdle();

    window.speechSynthesis.speak(fala);
}

// =========================
// 📤 ENVIAR
// =========================
async function enviar() {
    const input = document.getElementById("input");
    const texto = input.value.trim();

    if (!texto) return;

    mostrarMensagem("Você", texto, "user");
    input.value = "";

    estadoThinking();

    try {
        const resposta = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mensagem: texto })
        });

        const data = await resposta.json();

        mostrarMensagem("Jarvis", data.resposta, "jarvis");
        falarTexto(data.resposta);

    } catch {
        const msg = "Tive um problema na conexão.";
        mostrarMensagem("Jarvis", msg, "jarvis");
        falarTexto(msg);
    }
}

// =========================
// 🎤 VOZ
// =========================
function configurarVoz() {
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    const voiceBtn = document.getElementById("voiceBtn");
    const input = document.getElementById("input");

    if (!SpeechRecognition) {
        voiceBtn.addEventListener("click", () => {
            mostrarMensagem("Jarvis", "Reconhecimento de voz não suportado.", "jarvis");
        });
        return;
    }

    recognition = new SpeechRecognition();
    recognition.lang = "pt-BR";
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onstart = () => {
        ouvindo = true;
        voiceBtn.classList.add("ouvindo");
        input.placeholder = "Ouvindo...";
    };

    recognition.onresult = (event) => {
        let textoFinal = "";
        let textoParcial = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const texto = event.results[i][0].transcript;

            if (event.results[i].isFinal) textoFinal += texto;
            else textoParcial += texto;
        }

        input.value = textoFinal || textoParcial;

        if (textoFinal.trim()) {
            setTimeout(enviar, 250);
        }
    };

    recognition.onend = () => {
        ouvindo = false;
        voiceBtn.classList.remove("ouvindo");
        input.placeholder = "Mensagem";
    };

    voiceBtn.addEventListener("click", () => {
        if (ouvindo) return recognition.stop();

        window.speechSynthesis.cancel();

        try {
            recognition.start();
        } catch {
            recognition.stop();
        }
    });
}

// =========================
// 📍 LOCALIZAÇÃO
// =========================
async function buscarLocalizacaoServidor() {
    try {
        const r = await fetch("/api/localizacao/servidor");
        const d = await r.json();
        return d.ok && d.cidade ? `Base: ${d.cidade}` : "Base: indisponível";
    } catch {
        return "Base: indisponível";
    }
}

async function buscarLocalizacaoDispositivo() {
    if (!("geolocation" in navigator)) return "Você: indisponível";

    return new Promise((resolve) => {
        navigator.geolocation.getCurrentPosition(
            async (pos) => {
                try {
                    const r = await fetch("/api/localizacao/dispositivo", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            latitude: pos.coords.latitude,
                            longitude: pos.coords.longitude
                        })
                    });

                    const d = await r.json();
                    resolve(d.ok && d.cidade ? `Você: ${d.cidade}` : "Você: indisponível");
                } catch {
                    resolve("Você: indisponível");
                }
            },
            () => resolve("Você: bloqueado")
        );
    });
}

async function atualizarTickerLocalizacao() {
    const ticker = document.getElementById("tickerText");
    ticker.innerText = "Jarvis online • Localizando...";

    const [user, base] = await Promise.all([
        buscarLocalizacaoDispositivo(),
        buscarLocalizacaoServidor()
    ]);

    ticker.innerText = `Jarvis online • ${user} • ${base}`;
}

// =========================
// 🧭 MENU LATERAL
// =========================
function configurarMenu() {
    const openBtn = document.getElementById("openMenuBtn");
    const closeBtn = document.getElementById("closeMenuBtn");
    const menu = document.getElementById("sideMenu");
    const overlay = document.getElementById("menuOverlay");

    function abrir() {
        menu.classList.add("open");
        overlay.classList.remove("hidden");
    }

    function fechar() {
        menu.classList.remove("open");
        overlay.classList.add("hidden");
    }

    openBtn.addEventListener("click", abrir);
    closeBtn.addEventListener("click", fechar);
    overlay.addEventListener("click", fechar);
}

// =========================
// ⚙️ INIT
// =========================
async function configurarEventos() {
    const input = document.getElementById("input");
    const sendBtn = document.getElementById("sendBtn");

    await carregarAsciiGlobo();
    configurarPainelConfig();
    estadoIdle();

    sendBtn.addEventListener("click", enviar);

    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") enviar();
    });

    configurarVoz();
    configurarMenu();
    atualizarTickerLocalizacao();
}

document.addEventListener("DOMContentLoaded", configurarEventos);