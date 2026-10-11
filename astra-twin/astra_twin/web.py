"""Interface web privada para testar o Astra Twin através de localhost/Tailscale."""

from __future__ import annotations

import hmac
import os
import secrets
import time
from collections import defaultdict, deque
from functools import wraps
from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template_string, request, session, url_for

from .agent import AgentError, AstraTwinAgent
from .config import Settings
from .memory import MemoryStore

PAGE = r"""<!doctype html>
<html lang="pt-PT"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="color-scheme" content="dark light"><title>Astra Twin · Laboratório privado</title>
<style>
:root{font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#eaf0ff;background:#101522;font-synthesis:none}*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(ellipse at top,#1b2943 0,#101522 58%);padding:env(safe-area-inset-top) 14px env(safe-area-inset-bottom)}main{max-width:760px;margin:0 auto;padding:24px 0 40px}.brand{display:flex;align-items:center;gap:12px;margin:8px 0 22px}.mark{width:44px;height:44px;border-radius:14px;background:#293c60;display:grid;place-items:center;font-size:23px}.eyebrow{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#9eb6e8}.title{font-size:24px;font-weight:750;letter-spacing:-.04em;margin:2px 0}.sub{font-size:14px;color:#aab7ce}.panel{border:1px solid #2b3850;background:#151e2e;border-radius:20px;padding:16px;margin:14px 0;box-shadow:0 14px 40px #0002}.status{display:inline-flex;align-items:center;gap:7px;border:1px solid #315c53;color:#8fe1c3;background:#17342f;padding:7px 10px;border-radius:99px;font-size:12px}.dot{width:7px;height:7px;background:#62d9ae;border-radius:50%}.messages{display:flex;flex-direction:column;gap:12px;min-height:160px;max-height:55vh;overflow:auto;padding:4px 0 12px}.bubble{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.55;border-radius:15px;padding:12px 14px;max-width:94%;font-size:15px}.user{align-self:flex-end;background:#29436b;color:#fff}.assistant{align-self:flex-start;background:#202c40;border:1px solid #33435d}.muted{font-size:12px;color:#91a1bc}.composer{display:flex;flex-direction:column;gap:10px}.field{width:100%;border:1px solid #3a4962;border-radius:13px;background:#0e1522;color:#f4f7ff;font:inherit;font-size:16px;padding:13px;outline:none}.field:focus{border-color:#7fa5ed;box-shadow:0 0 0 3px #7fa5ed24}textarea.field{min-height:100px;resize:vertical}.actions{display:flex;gap:9px;flex-wrap:wrap}button{font:inherit;font-weight:650;border:0;border-radius:12px;padding:12px 16px;cursor:pointer}.primary{background:#a9c6ff;color:#12203b;flex:1}.secondary{background:#26334a;color:#dce6fa;border:1px solid #3a4962}.primary:disabled{opacity:.55;cursor:wait}.notice{color:#aebbd0;font-size:12px;line-height:1.5}.error{color:#ffaaa8}.login{max-width:420px;margin:10vh auto}.login label{display:block;margin:12px 0 6px;font-size:13px;color:#bfcee6}.foot{margin-top:18px;text-align:center;color:#71809b;font-size:11px}
</style></head><body><main>
{% if not authenticated %}<section class="panel login"><div class="brand"><div class="mark">✦</div><div><div class="eyebrow">Acesso privado</div><div class="title">Astra Twin</div></div></div><p class="sub">Laboratório de testes local. Introduz a palavra-passe configurada no dispositivo.</p>{% if error %}<p class="error">{{ error }}</p>{% endif %}<form method="post" action="/login"><input type="hidden" name="csrf_token" value="{{ csrf_token }}"><label for="password">Palavra-passe</label><input class="field" id="password" name="password" type="password" autocomplete="current-password" required autofocus><div style="height:12px"></div><button class="primary" style="width:100%">Entrar</button></form><p class="notice">A interface não publica a API do Ollama. O acesso depende também da rede privada autorizada.</p></section>
{% else %}<div class="brand"><div class="mark">✦</div><div><div class="eyebrow">Laboratório privado</div><div class="title">Astra Twin</div><div class="sub">Modelo local · {{ model }}</div></div></div><div class="status"><span class="dot"></span> Sessão autenticada</div><section class="panel"><div class="messages" id="messages" aria-live="polite"><div class="bubble assistant">Olá! Estou ligado ao modelo local. Faz uma pergunta para começar.</div></div><form class="composer" id="chat-form"><input type="hidden" id="csrf" value="{{ csrf_token }}"><label class="muted" for="prompt">A tua mensagem</label><textarea class="field" id="prompt" maxlength="12000" placeholder="Escreve uma pergunta…" required></textarea><div class="actions"><button class="primary" id="send" type="submit">Enviar pergunta</button><button class="secondary" id="clear" type="button">Nova conversa</button></div><div class="notice">As mensagens são processadas no Mac remoto pelo modelo local e podem ser guardadas na memória SQLite dessa sessão. Não introduzas palavras-passe ou dados sensíveis.</div></form></section><form method="post" action="/logout"><input type="hidden" name="csrf_token" value="{{ csrf_token }}"><button class="secondary" type="submit">Terminar sessão</button></form>{% endif %}<div class="foot">Astra Twin · Acesso privado · API Ollama não exposta diretamente</div></main>
{% if authenticated %}<script>
const form=document.getElementById('chat-form'),promptBox=document.getElementById('prompt'),messages=document.getElementById('messages'),send=document.getElementById('send'),csrf=document.getElementById('csrf').value;
function bubble(text,role){const el=document.createElement('div');el.className='bubble '+role;el.textContent=text;messages.appendChild(el);messages.scrollTop=messages.scrollHeight;return el;}
form.addEventListener('submit',async e=>{e.preventDefault();const text=promptBox.value.trim();if(!text)return;bubble(text,'user');promptBox.value='';send.disabled=true;send.textContent='A pensar…';const waiting=bubble('A gerar resposta local…','assistant');try{const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify({prompt:text})});const data=await res.json();if(!res.ok)throw new Error(data.error||'O pedido falhou.');waiting.textContent=data.answer;}catch(err){waiting.textContent='Erro: '+err.message;waiting.classList.add('error');}finally{send.disabled=false;send.textContent='Enviar pergunta';messages.scrollTop=messages.scrollHeight;promptBox.focus();}});
document.getElementById('clear').addEventListener('click',async()=>{if(!confirm('Começar uma nova conversa e limpar o histórico desta sessão?'))return;const res=await fetch('/api/clear',{method:'POST',headers:{'X-CSRF-Token':csrf}});if(res.ok){messages.replaceChildren();bubble('Nova conversa iniciada.','assistant');}else alert('Não foi possível limpar a sessão.');});
</script>{% endif %}</body></html>"""


def create_app(agent: AstraTwinAgent | None = None, password: str | None = None) -> Flask:
    from dotenv import load_dotenv
    load_dotenv()
    password = password if password is not None else os.getenv("ASTRA_TWIN_WEB_PASSWORD", "")
    secret_key = os.getenv("ASTRA_TWIN_WEB_SECRET", "")
    if len(password) < 16:
        raise RuntimeError("Define ASTRA_TWIN_WEB_PASSWORD com pelo menos 16 caracteres no .env.")
    if len(secret_key) < 32:
        raise RuntimeError("Define ASTRA_TWIN_WEB_SECRET com pelo menos 32 caracteres no .env.")

    app = Flask(__name__)
    app.secret_key = secret_key
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_SECURE=os.getenv("ASTRA_TWIN_WEB_COOKIE_SECURE", "0") == "1",
        MAX_CONTENT_LENGTH=16 * 1024,
        PERMANENT_SESSION_LIFETIME=3600,
    )
    settings = Settings.from_env()
    if agent is None:
        if settings.provider != "ollama":
            raise RuntimeError("A interface web exige ASTRA_TWIN_PROVIDER=ollama por segurança.")
        agent = AstraTwinAgent(settings, MemoryStore(settings.database_path))
    app.extensions["astra_agent"] = agent
    app.extensions["astra_password"] = password
    app.extensions["astra_limits"] = defaultdict(deque)

    def csrf_token() -> str:
        token = session.get("csrf_token")
        if not token:
            token = secrets.token_urlsafe(32)
            session["csrf_token"] = token
        return token

    def require_auth(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if session.get("authenticated") is not True:
                if request.path.startswith("/api/"):
                    return jsonify(error="Sessão terminada. Inicia sessão novamente."), 401
                return redirect(url_for("index"))
            return fn(*args, **kwargs)
        return wrapped

    def require_csrf() -> None:
        supplied = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
        expected = session.get("csrf_token", "")
        if not expected or not supplied or not hmac.compare_digest(supplied, expected):
            abort(403)

    @app.after_request
    def security_headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        return response

    @app.get("/")
    def index():
        if session.get("authenticated") is True:
            csrf = csrf_token()
        else:
            csrf = csrf_token()
        return render_template_string(PAGE, authenticated=session.get("authenticated") is True,
                                      csrf_token=csrf, model=settings.model, error=None)

    @app.post("/login")
    def login():
        require_csrf()
        client_ip = request.remote_addr or "unknown"
        attempts = app.extensions["astra_limits"][client_ip]
        now = time.monotonic()
        while attempts and now - attempts[0] > 300:
            attempts.popleft()
        if len(attempts) >= 8:
            abort(429)
        attempts.append(now)
        submitted = request.form.get("password", "")
        if not hmac.compare_digest(submitted, app.extensions["astra_password"]):
            session.clear()
            session["csrf_token"] = secrets.token_urlsafe(32)
            return render_template_string(PAGE, authenticated=False, csrf_token=session["csrf_token"],
                                          model=settings.model, error="Palavra-passe inválida."), 401
        session.clear()
        session.permanent = True
        session["authenticated"] = True
        session["csrf_token"] = secrets.token_urlsafe(32)
        session["chat_id"] = secrets.token_urlsafe(18)
        return redirect(url_for("index"), code=303)

    @app.post("/logout")
    @require_auth
    def logout():
        require_csrf()
        session.clear()
        return redirect(url_for("index"), code=303)

    @app.post("/api/chat")
    @require_auth
    def chat():
        require_csrf()
        data = request.get_json(silent=True) or {}
        prompt = data.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return jsonify(error="Escreve uma pergunta antes de enviar."), 400
        if len(prompt) > settings.max_input_chars:
            return jsonify(error=f"O limite é {settings.max_input_chars} caracteres."), 413
        answer = agent.ask(prompt, session_id="web-" + session["chat_id"])
        return jsonify(answer=answer, model=settings.model)

    @app.post("/api/clear")
    @require_auth
    def clear():
        require_csrf()
        agent.memory.clear_session("web-" + session["chat_id"])
        session["chat_id"] = secrets.token_urlsafe(18)
        return jsonify(ok=True)

    @app.get("/healthz")
    def health():
        return jsonify(status="ok", provider="ollama", model=settings.model), 200

    return app


def main() -> None:
    from werkzeug.serving import run_simple

    try:
        app = create_app()
    except (RuntimeError, ValueError, AgentError) as exc:
        raise SystemExit(f"Não foi possível iniciar a interface: {exc}") from exc
    host = os.getenv("ASTRA_TWIN_WEB_HOST", "127.0.0.1")
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("Por segurança, a interface só pode escutar em localhost.")
    port = int(os.getenv("ASTRA_TWIN_WEB_PORT", "8765"))
    print(f"Astra Twin web disponível apenas no próprio dispositivo: http://127.0.0.1:{port}")
    run_simple(host, port, app, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
