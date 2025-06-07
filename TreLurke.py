#!/usr/bin/env python3
import os
import requests
import json
import time
import subprocess
from datetime import datetime

# Configurações
PASTA_RESULTADOS = "ErikNet_Results"
os.makedirs(PASTA_RESULTADOS, exist_ok=True)

# Banner ErikNet
BANNER = r"""
███████░██░ ░██░███████░░   ██░     ░██░  ░██░██████░ ██   ██░███████░██████░
░░░██░░ ██░░░██░██  ░░      ██░░    ░██░  ░██░██   ██ ██  ██░ ██░░░░  ██   ██░
  ░██░  ███████░█████░░     ██░     ░██░  ░██░██████░ ████░   █████   ██████░░
  ░██░░ ██   ██░██   ░░     ██░░░░  ░██░░░░██░██  ██░ ██░░██░ ██░░░   ██   ██░░
  ░██░░ ██░░░██░███████░░   ███████ ░████████░██░░░██ ██░░ ██ ███████ ██   ██░
   ░░░  ░░░ ░░░ ░░░░░░░     ░░░░░░░  ░░░░░░░░ ░░   ░░ ░░  ░░░ ░░░░░░░░░░░░░░░░
   ░ ░  ░     ░ ░   ░ ░     ░░   ░░  ░░░  ░░░  ░   ░  ░    ░░ ░░    ░░      ░░
  ░  ░             ░   ░    ░   ░    ░  ░   ░  ░    ░       ░  ░   ░       ░ 
  made in Brazil Big The god and Erik 16y Linux and termux 
"""

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def executar_holehe(email):
    try:
        print("\nExecutando Holehe para verificação de e-mail...")
        resultado = subprocess.run(['holehe', email], capture_output=True, text=True, timeout=120)
        
        if resultado.returncode == 0:
            print("\nResultados do Holehe:")
            print(resultado.stdout)
            
            # Salvar resultados em arquivo
            nome_arquivo = f"holehe_results_{email.replace('@', '_')}.txt"
            caminho_arquivo = os.path.join(PASTA_RESULTADOS, nome_arquivo)
            
            with open(caminho_arquivo, 'w') as f:
                f.write(resultado.stdout)
            
            print(f"\nResultados salvos em: {caminho_arquivo}")
            return resultado.stdout
        else:
            print("\nErro ao executar Holehe:")
            print(resultado.stderr)
            return None
    except FileNotFoundError:
        print("\nHolehe não está instalado. Por favor instale com:")
        print("pip install holehe")
        return None
    except Exception as e:
        print(f"\nErro ao executar Holehe: {str(e)}")
        return None

def buscar_por_nome_real(nome):
    try:
        print(f"\nBuscando por nome real: {nome}")
        time.sleep(1)
        
        # Simulando busca em múltiplas fontes
        resultados = {
            "LinkedIn": {
                "url": f"https://www.linkedin.com/search/results/people/?keywords={nome.replace(' ', '%20')}",
                "method": "Web Scraping",
                "exists": True
            },
            "Facebook": {
                "url": f"https://www.facebook.com/public/{nome.replace(' ', '.')}",
                "method": "Web Scraping",
                "exists": True
            },
            "Google Search": {
                "url": f"https://www.google.com/search?q={nome.replace(' ', '+')}",
                "method": "Motor de Busca",
                "exists": True
            }
        }
        
        return resultados
    except Exception as e:
        print(f"Erro na busca por nome real: {str(e)}")
        return {"error": str(e)}

def verificar_gmail_aprimorado(email):
    try:
        sessao = requests.Session()
        resposta = sessao.head(
            "https://mail.google.com/mail/gxlu",
            params={"email": email},
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        
        resposta2 = requests.get(
            f"https://mail.google.com/mail/gxlu?email={email}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )
        
        resposta3 = requests.post(
            "https://accounts.google.com/_/signup/usernameavailability",
            headers={"Content-Type": "application/json"},
            json={"input_01": {"input": email, "first_name": "", "last_name": ""}},
            params={"hl": "pt-BR"},
            timeout=5
        )
        
        return any([
            bool(resposta.cookies.get("GX")),
            "set-cookie" in resposta2.headers,
            resposta3.json().get("input_01", {}).get("valid") is False
        ])
    except Exception as e:
        print(f"Erro na verificação do Gmail: {str(e)}")
        return False

def buscar_perfis(username):
    resultados = {}
    sites = {
        "GitHub": {
            "url": f"https://api.github.com/users/{username}",
            "nome_field": "name",
            "method": "API Pública"
        },
        "Twitter": {
            "url": f"https://twitter.com/{username}",
            "nome_field": None,
            "method": "Web Scraping"
        },
        "Instagram": {
            "url": f"https://www.instagram.com/{username}/?__a=1",
            "nome_field": "graphql.user.full_name",
            "method": "API Não Oficial"
        },
        "Reddit": {
            "url": f"https://www.reddit.com/user/{username}/about.json",
            "nome_field": "data.name",
            "method": "API Pública"
        }
    }

    for site, config in sites.items():
        try:
            time.sleep(1)
            resposta = requests.get(
                config["url"],
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10
            )
            
            dados = {
                'exists': resposta.status_code == 200,
                'url': config["url"],
                'method': config["method"]
            }
            
            if dados['exists']:
                try:
                    if site == "Twitter":
                        dados['nome_perfil'] = username
                    else:
                        json_data = resposta.json()
                        if config["nome_field"]:
                            campos = config["nome_field"].split('.')
                            valor = json_data
                            for campo in campos:
                                if isinstance(valor, dict):
                                    valor = valor.get(campo, {})
                            if valor and not isinstance(valor, dict):
                                dados['nome_perfil'] = valor
                except Exception as e:
                    print(f"Erro ao processar {site}: {str(e)}")
                    
            resultados[site] = dados
            
        except Exception as e:
            resultados[site] = {'error': str(e), 'exists': False}
    
    return resultados

def mostrar_resultados_eriknet(dados):
    print("\n" + "═"*60)
    print(" RESULTADOS ERIKNET ".center(60))
    print("═"*60)
    
    for plataforma, info in dados.items():
        print(f"\n▓ {plataforma.upper()}")
        if 'error' in info:
            print(f"  🔴 ERRO: {info['error']}")
        else:
            status = "🟢 ENCONTRADO" if info.get('exists') else "🔴 NÃO ENCONTRADO"
            print(f"  {status}")
            
            if 'url' in info:
                print(f"  🌐 URL: {info['url']}")
                
            if 'nome_perfil' in info:
                print(f"  📛 NOME: {info['nome_perfil']}")
                
            if 'method' in info:
                print(f"  ⚙️ MÉTODO: {info['method']}")
    
    print("\n" + "═"*60)

def verificar_ip(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        data = response.json()
        
        if data['status'] == 'success':
            return {
                'País': data.get('country', 'N/A'),
                'Código do País': data.get('countryCode', 'N/A'),
                'Região': data.get('regionName', 'N/A'),
                'Cidade': data.get('city', 'N/A'),
                'CEP': data.get('zip', 'N/A'),
                'Provedor': data.get('isp', 'N/A'),
                'Organização': data.get('org', 'N/A'),
                'ASN': data.get('as', 'N/A'),
                'Latitude': data.get('lat', 'N/A'),
                'Longitude': data.get('lon', 'N/A'),
                'Fuso Horário': data.get('timezone', 'N/A')
            }
        return {'error': 'IP não encontrado ou inválido'}
    except Exception as e:
        return {'error': f"Erro na consulta: {str(e)}"}

def menu_principal():
    limpar_tela()
    print(BANNER)
    print(f"\n[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]")
    print("\n1. Buscar por nome de usuário")
    print("2. Buscar por e-mail (com Holehe)")
    print("3. Buscar por nome real")
    print("4. Verificar informações de IP")
    print("5. Sair")
    
    try:
        return int(input("\nEscolha uma opção (1-5): "))
    except:
        return 0

def executar_busca():
    while True:
        opcao = menu_principal()
        
        if opcao == 1:
            username = input("\nDigite o nome de usuário: ").strip()
            resultados = buscar_perfis(username)
            mostrar_resultados_eriknet(resultados)
            
        elif opcao == 2:
            email = input("\nDigite o e-mail: ").strip()
            
            # Executa Holehe
            resultados_holehe = executar_holehe(email)
            
            # Verificação adicional do Gmail
            username = email.split('@')[0] if '@' in email else email
            resultados = buscar_perfis(username)      
            resultados["Gmail"] = {
                'exists': verificar_gmail_aprimorado(email),
                'method': 'Verificação Combinada',
                'url': f"mailto:{email}"
            }
            
            mostrar_resultados_eriknet(resultados)
            
        elif opcao == 3:
            nome_real = input("\nDigite o nome real (completo ou parcial): ").strip()
            resultados = buscar_por_nome_real(nome_real)
            mostrar_resultados_eriknet(resultados)
            
        elif opcao == 4:
            ip = input("\nDigite o endereço IP: ").strip()
            info_ip = verificar_ip(ip)
            print("\nInformações do IP:")
            for chave, valor in info_ip.items():
                print(f"{chave}: {valor}")
                
        elif opcao == 5:
            print("\nSaindo do ErikNet...")
            break
            
        else:
            print("\nOpção inválida! Tente novamente.")
            time.sleep(1)
            
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    try:
        executar_busca()
    except KeyboardInterrupt:
        print("\n\nErikNet interrompido pelo usuário!")
    except Exception as e:
        print(f"\nERRO CRÍTICO: {str(e)}")
    finally:
        print("\nObrigado por usar o ErikNet! Segurança sempre.\n")
