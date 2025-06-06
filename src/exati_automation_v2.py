#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
import base64
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import openpyxl
from io import BytesIO
import tempfile
import uuid
from PIL import Image

class ExatiAutomation:
    def __init__(self, sharepoint_url=None, exati_url=None, exati_username=None, exati_password=None, 
                 current_user=None, static_dir=None):
        """Inicializa a automação do Exati."""
        self.sharepoint_url = sharepoint_url
        self.exati_url = exati_url
        self.exati_username = exati_username
        self.exati_password = exati_password
        self.current_user = current_user
        self.static_dir = static_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        
        self.driver = None
        self.points = []
        self.current_point_index = 0
        self.log_messages = []
        
        # Garante que o diretório static existe
        if not os.path.exists(self.static_dir):
            os.makedirs(self.static_dir)
        
    def add_log(self, message):
        """Adiciona uma mensagem ao log."""
        self.log_messages.append(message)
        print(message)
        
    def initialize(self):
        """Inicializa a automação, conectando ao SharePoint e ao Exati."""
        try:
            self.add_log(f"Iniciando automação para o usuário: {self.current_user}")
            
            # Inicializa o navegador
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.add_log("Navegador inicializado.")
            
            # Lê a planilha do SharePoint
            self.read_sharepoint_data()
            
            # Conecta ao Exati
            self.login_to_exati()
            
            # Configura a interface do Exati
            self.configure_exati_interface()
            
            # Busca os pontos do usuário
            self.points = self.get_user_points()
            
            if not self.points:
                self.add_log(f"Nenhum ponto encontrado para o usuário {self.current_user}.")
                return False
                
            self.add_log(f"Encontrados {len(self.points)} pontos para processamento.")
            return True
            
        except Exception as e:
            self.add_log(f"Erro ao inicializar automação: {str(e)}")
            if self.driver:
                self.driver.quit()
            return False
            
    def read_sharepoint_data(self):
        """Lê os dados da planilha do SharePoint."""
        try:
            self.add_log("Lendo dados da planilha do SharePoint...")
            
            # Em uma implementação real, aqui você leria a planilha do SharePoint
            # usando a biblioteca office365-rest-python-client
            
            # Para desenvolvimento e teste, vamos simular a leitura da planilha
            # com base nas capturas de tela fornecidas
            
            # Simula os dados da planilha
            self.sharepoint_data = [
                {"id": "21459", "status": "CORRIGIDO", "user": "Douglas", "potencia": "30", "verificacao": "30"},
                {"id": "21090", "status": "CORRIGIDO", "user": "Douglas", "potencia": "62", "verificacao": "30"},
                {"id": "12786", "status": "AUDITADO", "user": "Douglas", "potencia": "213", "verificacao": "ok"},
                {"id": "12787", "status": "AUDITADO", "user": "Douglas", "potencia": "213", "verificacao": "ok"},
                {"id": "12790", "status": "AUDITADO", "user": "Douglas", "potencia": "213", "verificacao": "ok"},
                {"id": "12791", "status": "AUDITADO", "user": "Douglas", "potencia": "213", "verificacao": "ok"},
                {"id": "12792", "status": "AUDITADO", "user": "Douglas", "potencia": "213", "verificacao": "ok"},
                {"id": "12834", "status": "AUDITADO", "user": "Douglas", "potencia": "213", "verificacao": "ok"},
                {"id": "12814", "status": "AUDITADO", "user": "Douglas", "potencia": "213", "verificacao": "ok"},
                {"id": "12844", "status": "", "user": "Douglas", "potencia": "213", "verificacao": ""},
                {"id": "12854", "status": "AUDITADO", "user": "Douglas", "potencia": "213", "verificacao": "ok"},
                {"id": "12866", "status": "AUDITADO", "user": "Douglas", "potencia": "213", "verificacao": "ok"},
                {"id": "75575", "status": "AUDITADO", "user": "Satornello", "potencia": "130", "verificacao": "ok"},
                {"id": "75576", "status": "AUDITADO", "user": "Satornello", "potencia": "130", "verificacao": "ok"},
                {"id": "75577", "status": "AUDITADO", "user": "Satornello", "potencia": "130", "verificacao": "ok"},
                {"id": "75578", "status": "AUDITADO", "user": "Satornello", "potencia": "130", "verificacao": "ok"},
                {"id": "75580", "status": "AUDITADO", "user": "Satornello", "potencia": "130", "verificacao": "ok"},
                {"id": "75581", "status": "AUDITADO", "user": "Satornello", "potencia": "130", "verificacao": "ok"},
                {"id": "75582", "status": "AUDITADO", "user": "Satornello", "potencia": "130", "verificacao": "ok"},
                {"id": "75584", "status": "AUDITADO", "user": "Satornello", "potencia": "130", "verificacao": "ok"},
                {"id": "75590", "status": "AUDITADO", "user": "Satornello", "potencia": "130", "verificacao": "ok"},
                {"id": "75617", "status": "CORRIGIDO", "user": "Satornello", "potencia": "130", "verificacao": "150"}
            ]
            
            self.add_log(f"Dados da planilha lidos com sucesso. {len(self.sharepoint_data)} registros encontrados.")
            
        except Exception as e:
            self.add_log(f"Erro ao ler dados do SharePoint: {str(e)}")
            raise
            
    def login_to_exati(self):
        """Faz login no sistema Exati."""
        try:
            self.add_log("Conectando ao Exati...")
            
            # Navega para a página de login
            self.driver.get(self.exati_url)
            
            # Aguarda a página carregar
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Preenche o formulário de login
            self.driver.find_element(By.ID, "username").send_keys(self.exati_username)
            self.driver.find_element(By.ID, "password").send_keys(self.exati_password)
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # Aguarda o login ser concluído
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'exati')]"))
            )
            
            self.add_log("Login realizado com sucesso.")
            
        except Exception as e:
            self.add_log(f"Erro ao fazer login no Exati: {str(e)}")
            raise
    
    def configure_exati_interface(self):
        """Configura a interface do Exati conforme necessário."""
        try:
            self.add_log("Configurando interface do Exati...")
            
            # Clica no ícone de localização para abrir o menu de pontos de serviço
            location_icon = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'location-icon')]"))
            )
            location_icon.click()
            
            # Aguarda o menu abrir
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[text()='Pontos de serviços']"))
            )
            
            # Seleciona o parque de serviço "Curitiba"
            dropdown = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Parque de Serviço')]//following-sibling::div//select"))
            )
            dropdown.click()
            
            curitiba_option = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//option[contains(text(), 'Curitiba')]"))
            )
            curitiba_option.click()
            
            # Marca as opções necessárias
            checkboxes = {
                "Exibir Plaquetas": True,
                "Pontos de interesse": False,
                "Pontos Cadastrados": True,
                "Ponto IP": True,
                "Ponto IP Modernização": True
            }
            
            for label, checked in checkboxes.items():
                try:
                    checkbox = self.driver.find_element(By.XPATH, f"//span[contains(text(), '{label}')]//preceding-sibling::input")
                    if (checkbox.is_selected() and not checked) or (not checkbox.is_selected() and checked):
                        checkbox.click()
                except:
                    self.add_log(f"Não foi possível encontrar ou marcar a opção: {label}")
            
            self.add_log("Interface do Exati configurada com sucesso.")
            
        except Exception as e:
            self.add_log(f"Erro ao configurar interface do Exati: {str(e)}")
            raise
            
    def get_user_points(self):
        """Obtém os pontos associados ao usuário atual da planilha."""
        try:
            self.add_log(f"Buscando pontos do usuário {self.current_user}...")
            
            # Filtra os pontos pelo usuário atual e que não tenham verificação
            user_points = [
                point for point in self.sharepoint_data 
                if point["user"] == self.current_user and not point["verificacao"]
            ]
            
            self.add_log(f"Encontrados {len(user_points)} pontos pendentes para o usuário {self.current_user}.")
            return user_points
            
        except Exception as e:
            self.add_log(f"Erro ao buscar pontos do usuário: {str(e)}")
            return []
            
    def get_point_images(self, point_id):
        """Obtém as imagens associadas a um ponto no Exati."""
        try:
            self.add_log(f"Buscando imagens para o ponto {point_id}...")
            
            # Navega para a página de pontos de serviço
            self.driver.get(f"{self.exati_url}/pontos-de-servicos")
            
            # Aguarda a página carregar
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Buscar']"))
            )
            
            # Busca o ponto pelo ID
            search_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Buscar']")
            search_input.clear()
            search_input.send_keys(point_id)
            
            # Clica no botão de busca
            search_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@title='Buscar']"))
            )
            search_button.click()
            
            # Aguarda os resultados
            time.sleep(2)  # Espera adicional para garantir que os resultados sejam carregados
            
            # Clica no botão "Visualizar" do resultado
            visualize_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visualizar')]"))
            )
            visualize_button.click()
            
            # Aguarda a página do ponto carregar
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'FOTOS')]"))
            )
            
            # Clica na aba de fotos
            photos_tab = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'FOTOS')]"))
            )
            photos_tab.click()
            
            # Aguarda as fotos carregarem
            time.sleep(2)  # Espera adicional para garantir que as fotos sejam carregadas
            
            # Captura todas as imagens
            image_elements = self.driver.find_elements(By.XPATH, "//img[contains(@src, 'blob:')]")
            
            if not image_elements:
                self.add_log(f"Nenhuma imagem encontrada para o ponto {point_id}.")
                return []
            
            # Captura as imagens e salva localmente
            image_paths = []
            for i, img in enumerate(image_elements):
                try:
                    # Captura a imagem como base64
                    img_base64 = self.driver.execute_script("""
                        var img = arguments[0];
                        var canvas = document.createElement('canvas');
                        canvas.width = img.naturalWidth;
                        canvas.height = img.naturalHeight;
                        var ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0);
                        return canvas.toDataURL('image/png').substring(22);
                    """, img)
                    
                    # Salva a imagem localmente
                    img_path = os.path.join(self.static_dir, f"point_{point_id}_img_{i}.png")
                    
                    # Decodifica e salva a imagem
                    with open(img_path, "wb") as f:
                        f.write(base64.b64decode(img_base64))
                    
                    image_paths.append(f"/static/point_{point_id}_img_{i}.png")
                    self.add_log(f"Imagem {i+1} capturada e salva para o ponto {point_id}.")
                    
                except Exception as e:
                    self.add_log(f"Erro ao capturar imagem {i+1} para o ponto {point_id}: {str(e)}")
            
            self.add_log(f"Encontradas {len(image_paths)} imagens para o ponto {point_id}.")
            return image_paths
            
        except Exception as e:
            self.add_log(f"Erro ao buscar imagens do ponto {point_id}: {str(e)}")
            return []
            
    def submit_verification(self, point_id, value):
        """Submete a verificação para um ponto."""
        try:
            self.add_log(f"Submetendo verificação para o ponto {point_id}: {value}")
            
            # Em uma implementação real, aqui você atualizaria a planilha
            # com o valor da verificação na coluna K
            
            # Simula a atualização da planilha
            for point in self.sharepoint_data:
                if point["id"] == point_id:
                    point["verificacao"] = value
                    break
                    
            return True
            
        except Exception as e:
            self.add_log(f"Erro ao submeter verificação: {str(e)}")
            return False
            
    def get_next_point(self):
        """Avança para o próximo ponto."""
        if self.current_point_index < len(self.points) - 1:
            self.current_point_index += 1
            point = self.points[self.current_point_index]
            point_id = point["id"]
            self.add_log(f"Avançando para o ponto {point_id}...")
            return point_id
        else:
            self.add_log("Todos os pontos foram processados.")
            return None
            
    def get_current_point(self):
        """Retorna o ponto atual."""
        if self.points and self.current_point_index < len(self.points):
            return self.points[self.current_point_index]["id"]
        return None
            
    def close(self):
        """Fecha o navegador e limpa os recursos."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            
    def scan_users(self):
        """Escaneia os usuários da planilha."""
        try:
            self.add_log("Escaneando usuários da planilha...")
            
            # Lê a planilha se ainda não foi lida
            if not hasattr(self, 'sharepoint_data'):
                self.read_sharepoint_data()
            
            # Extrai os nomes únicos da coluna de usuários
            users = list(set(point["user"] for point in self.sharepoint_data))
            
            self.add_log(f"Encontrados {len(users)} usuários na planilha.")
            return users
            
        except Exception as e:
            self.add_log(f"Erro ao escanear usuários: {str(e)}")
            return []
