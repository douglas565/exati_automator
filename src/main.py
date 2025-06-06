#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, url_for
import os
import sys
import json
import pandas as pd
import requests
from exati_automation_v2 import ExatiAutomation  # Importação relativa corrigida

# Configuração correta para encontrar os templates
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Estado da automação
automation_state = {
    "running": False,
    "paused": False,
    "current_id": None,
    "image_urls": [],  # Lista de URLs de imagens para o ponto atual
    "progress": "Idle",
    "log": [],
    "current_user": None,
    "current_image_index": 0,  # Índice da imagem atual sendo exibida
    "total_images": 0  # Total de imagens para o ponto atual
}

# Instância da automação
automation_instance = None

@app.route('/')
def index():
    """Renderiza a página principal."""
    return render_template('index.html', state=automation_state)

@app.route('/scan_users', methods=['POST'])
def scan_users():
    """Escaneia os usuários da planilha."""
    global automation_instance
    
    try:
        data = request.json
        sharepoint_url = data.get('sharepoint_url')
        exati_url = data.get('exati_url')
        exati_username = data.get('exati_username')
        exati_password = data.get('exati_password')
        
        # Inicializa a automação temporariamente para escanear usuários
        temp_automation = ExatiAutomation(
            sharepoint_url=sharepoint_url,
            exati_url=exati_url,
            exati_username=exati_username,
            exati_password=exati_password,
            static_dir=static_dir
        )
        
        # Escaneia os usuários
        users = temp_automation.scan_users()
        
        if not users:
            return jsonify({
                "status": "error",
                "message": "Nenhum usuário encontrado na planilha."
            }), 404
        
        return jsonify({
            "status": "success",
            "users": users,
            "message": f"Encontrados {len(users)} usuários na planilha."
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro ao escanear usuários: {str(e)}"
        }), 500

@app.route('/start', methods=['POST'])
def start_automation():
    """Inicia o processo de automação."""
    global automation_instance
    
    try:
        data = request.json
        sharepoint_url = data.get('sharepoint_url')
        exati_url = data.get('exati_url')
        exati_username = data.get('exati_username')
        exati_password = data.get('exati_password')
        sharepoint_username = data.get('sharepoint_username')
        sharepoint_password = data.get('sharepoint_password')
        current_user = data.get('current_user')
        
        # Limpa o estado anterior
        automation_state['running'] = False
        automation_state['paused'] = False
        automation_state['current_id'] = None
        automation_state['image_urls'] = []
        automation_state['progress'] = "Inicializando..."
        automation_state['log'] = []
        automation_state['current_user'] = current_user
        automation_state['current_image_index'] = 0
        automation_state['total_images'] = 0
        
        # Fecha a instância anterior se existir
        if automation_instance:
            automation_instance.close()
        
        # Cria uma nova instância da automação
        automation_instance = ExatiAutomation(
            sharepoint_url=sharepoint_url,
            exati_url=exati_url,
            exati_username=exati_username,
            exati_password=exati_password,
            current_user=current_user,
            static_dir=static_dir
        )
        
        # Inicializa a automação
        success = automation_instance.initialize()
        
        if not success:
            return jsonify({
                "status": "error",
                "message": "Falha ao inicializar a automação.",
                "state": get_current_state()
            }), 500
        
        # Atualiza o estado
        automation_state['running'] = True
        automation_state['log'] = automation_instance.log_messages
        
        # Carrega o primeiro ponto
        current_point = automation_instance.get_current_point()
        
        if not current_point:
            automation_state['running'] = False
            return jsonify({
                "status": "error",
                "message": f"Nenhum ponto encontrado para o usuário {current_user}.",
                "state": get_current_state()
            }), 404
        
        # Atualiza o estado com as informações do ponto
        automation_state['current_id'] = current_point
        
        # Busca as imagens do ponto
        image_urls = automation_instance.get_point_images(current_point)
        
        automation_state['image_urls'] = image_urls
        automation_state['current_image_index'] = 0
        automation_state['total_images'] = len(image_urls)
        automation_state['progress'] = f"Processando 1 de {len(automation_instance.points)}"
        automation_state['log'] = automation_instance.log_messages
        
        return jsonify({
            "status": "success", 
            "message": "Automação iniciada com sucesso.", 
            "state": get_current_state()
        })
        
    except Exception as e:
        if automation_instance:
            automation_instance.close()
            automation_instance = None
        
        automation_state['running'] = False
        add_log(f"Erro ao iniciar automação: {str(e)}")
        
        return jsonify({
            "status": "error", 
            "message": f"Erro ao iniciar automação: {str(e)}", 
            "state": get_current_state()
        }), 500

@app.route('/submit_verification', methods=['POST'])
def submit_verification():
    """Processa a verificação do usuário e avança para o próximo ponto."""
    global automation_instance
    
    if not automation_state['running'] or automation_state['paused'] or not automation_instance:
        return jsonify({
            "status": "error", 
            "message": "Automação não está em execução ou está pausada.", 
            "state": get_current_state()
        }), 400

    try:
        data = request.json
        verification_value = data.get('value')  # 'ok' ou valor de potência
        current_id = automation_state['current_id']
        
        # Submete a verificação
        success = automation_instance.submit_verification(current_id, verification_value)
        
        if not success:
            return jsonify({
                "status": "error", 
                "message": "Falha ao submeter verificação.", 
                "state": get_current_state()
            }), 500
        
        # Avança para o próximo ponto
        next_point_id = automation_instance.get_next_point()
        
        if not next_point_id:
            # Não há mais pontos para processar
            automation_state['running'] = False
            automation_state['current_id'] = None
            automation_state['image_urls'] = []
            automation_state['progress'] = "Concluído"
            automation_state['log'] = automation_instance.log_messages
            
            # Fecha o navegador
            automation_instance.close()
            automation_instance = None
            
            return jsonify({
                "status": "success", 
                "message": "Todos os pontos foram processados.", 
                "state": get_current_state()
            })
        
        # Atualiza o estado com as informações do próximo ponto
        automation_state['current_id'] = next_point_id
        
        # Busca as imagens do próximo ponto
        image_urls = automation_instance.get_point_images(next_point_id)
        
        automation_state['image_urls'] = image_urls
        automation_state['current_image_index'] = 0
        automation_state['total_images'] = len(image_urls)
        automation_state['progress'] = f"Processando {automation_instance.current_point_index + 1} de {len(automation_instance.points)}"
        automation_state['log'] = automation_instance.log_messages
        
        return jsonify({
            "status": "success", 
            "message": "Verificação submetida com sucesso.", 
            "state": get_current_state()
        })
        
    except Exception as e:
        add_log(f"Erro ao processar verificação: {str(e)}")
        
        return jsonify({
            "status": "error", 
            "message": f"Erro ao processar verificação: {str(e)}", 
            "state": get_current_state()
        }), 500

@app.route('/next_image', methods=['POST'])
def next_image():
    """Avança para a próxima imagem do ponto atual."""
    if not automation_state['running'] or automation_state['paused']:
        return jsonify({
            "status": "error", 
            "message": "Automação não está em execução ou está pausada.", 
            "state": get_current_state()
        }), 400
    
    if automation_state['total_images'] <= 1:
        return jsonify({
            "status": "error", 
            "message": "Não há mais imagens para este ponto.", 
            "state": get_current_state()
        }), 400
    
    # Avança para a próxima imagem
    automation_state['current_image_index'] = (automation_state['current_image_index'] + 1) % automation_state['total_images']
    
    add_log(f"Exibindo imagem {automation_state['current_image_index'] + 1} de {automation_state['total_images']}")
    
    return jsonify({
        "status": "success", 
        "message": "Avançado para a próxima imagem.", 
        "state": get_current_state()
    })

@app.route('/prev_image', methods=['POST'])
def prev_image():
    """Retorna para a imagem anterior do ponto atual."""
    if not automation_state['running'] or automation_state['paused']:
        return jsonify({
            "status": "error", 
            "message": "Automação não está em execução ou está pausada.", 
            "state": get_current_state()
        }), 400
    
    if automation_state['total_images'] <= 1:
        return jsonify({
            "status": "error", 
            "message": "Não há mais imagens para este ponto.", 
            "state": get_current_state()
        }), 400
    
    # Retorna para a imagem anterior
    automation_state['current_image_index'] = (automation_state['current_image_index'] - 1) % automation_state['total_images']
    
    add_log(f"Exibindo imagem {automation_state['current_image_index'] + 1} de {automation_state['total_images']}")
    
    return jsonify({
        "status": "success", 
        "message": "Retornado para a imagem anterior.", 
        "state": get_current_state()
    })

@app.route('/pause', methods=['POST'])
def pause_automation():
    """Pausa a automação."""
    if automation_state['running'] and not automation_state['paused']:
        automation_state['paused'] = True
        add_log("Automação pausada.")
        return jsonify({
            "status": "success", 
            "message": "Automação pausada.", 
            "state": get_current_state()
        })
    return jsonify({
        "status": "error", 
        "message": "Não é possível pausar.", 
        "state": get_current_state()
    }), 400

@app.route('/resume', methods=['POST'])
def resume_automation():
    """Retoma a automação."""
    if automation_state['running'] and automation_state['paused']:
        automation_state['paused'] = False
        add_log("Automação retomada.")
        return jsonify({
            "status": "success", 
            "message": "Automação retomada.", 
            "state": get_current_state()
        })
    return jsonify({
        "status": "error", 
        "message": "Não é possível retomar.", 
        "state": get_current_state()
    }), 400

@app.route('/stop', methods=['POST'])
def stop_automation():
    """Para a automação."""
    global automation_instance
    
    if automation_state['running']:
        automation_state['running'] = False
        automation_state['paused'] = False
        automation_state['current_id'] = None
        automation_state['image_urls'] = []
        automation_state['progress'] = "Idle"
        add_log("Automação interrompida.")
        
        # Fecha o navegador
        if automation_instance:
            automation_instance.close()
            automation_instance = None
        
        return jsonify({
            "status": "success", 
            "message": "Automação interrompida.", 
            "state": get_current_state()
        })
    return jsonify({
        "status": "error", 
        "message": "Automação não está em execução.", 
        "state": get_current_state()
    }), 400

def add_log(message):
    """Adiciona uma mensagem ao log."""
    automation_state['log'].append(message)
    print(message)  # Para debug

def get_current_state():
    """Retorna o estado atual da automação."""
    return {
        "running": automation_state['running'],
        "paused": automation_state['paused'],
        "current_id": automation_state['current_id'],
        "image_urls": automation_state['image_urls'],
        "progress": automation_state['progress'],
        "log": automation_state['log'],
        "current_user": automation_state['current_user'],
        "current_image_index": automation_state['current_image_index'],
        "total_images": automation_state['total_images']
    }

if __name__ == '__main__':
    # Cria diretório static se não existir
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    print(f"Template directory: {template_dir}")
    print(f"Static directory: {static_dir}")
    print(f"Templates exist: {os.path.exists(template_dir)}")
    print(f"index.html exists: {os.path.exists(os.path.join(template_dir, 'index.html'))}")
    
    app.run(host='0.0.0.0', port=8080, debug=True)
