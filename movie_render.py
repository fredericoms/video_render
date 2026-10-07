import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def build_wealthlogic_video(audio_path: str, image_paths: list, output_path: str, fps: int = 24) -> None:
    """
    Gera um vídeo concatenando uma lista de imagens sincronizadas 
    ao longo da duração de um arquivo de áudio principal.
    
    Args:
        audio_path (str): Caminho para o arquivo de áudio (ex: locução em inglês).
        image_paths (list): Lista de caminhos para as imagens que comporão o vídeo.
        output_path (str): Caminho de destino para o vídeo renderizado (.mp4).
        fps (int): Taxa de quadros por segundo do vídeo de saída.
    """
    try:
        print(f"[{output_path}] Iniciando pipeline de processamento de mídia...")
        
        # 1. Carregar e validar a trilha de áudio
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Trilha de áudio ausente: {audio_path}")
            
        audio_clip = AudioFileClip(audio_path)
        total_duration = audio_clip.duration
        
        # 2. Calcular o fatiamento de tempo de tela (Screen Time)
        if not image_paths:
            raise ValueError("O array de imagens (assets visuais) não pode estar vazio.")
            
        duration_per_image = total_duration / len(image_paths)
        print(f"Duração total: {total_duration:.2f}s | Tempo por imagem: {duration_per_image:.2f}s")
        
        # 3. Instanciar e processar os nós visuais (ImageClips)
        video_clips = []
        for img_path in image_paths:
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Asset visual ausente: {img_path}")
            
            # Instancia o frame, define sua duração na timeline e assegura a resolução
            clip = ImageClip(img_path).set_duration(duration_per_image)
            video_clips.append(clip)
            
        # 4. Compilar a timeline visual (Merge)
        # O método 'compose' é mais tolerante caso as imagens tenham resoluções ligeiramente diferentes
        final_visual_timeline = concatenate_videoclips(video_clips, method="compose")
        
        # 5. Acoplar a stream de áudio à timeline de vídeo
        final_video = final_visual_timeline.set_audio(audio_clip)
        
        # 6. Processo de Encoding e I/O (Gravação do Arquivo)
        # Parâmetros otimizados para YouTube: H.264 (libx264) e AAC
        final_video.write_videofile(
            output_path, 
            fps=fps, 
            codec="libx264", 
            audio_codec="aac", 
            threads=4,               # Define o paralelismo do encoder (ajuste conforme os cores do seu CPU)
            preset="ultrafast",      # 'ultrafast' acelera a automação à custa de um arquivo levemente maior
            logger=None              # Desativa a barra de progresso do terminal caso rode em background
        )
        
        print(f"[{output_path}] Renderização concluída com sucesso (Exit Code 0).")
        
    except Exception as e:
        print(f"[FATAL] Falha no pipeline de renderização: {str(e)}")
        # Em um ambiente corporativo/nuvem, encaminhe esta string para o CloudWatch, Datadog, etc.
    
    finally:
        # Liberação de memória dos objetos carregados pelo ffmpeg sob o capô
        try:
            audio_clip.close()
            final_visual_timeline.close()
            final_video.close()
        except NameError:
            pass # Ignora caso a falha tenha ocorrido antes da alocação dos objetos

# ==========================================
# Ponto de Entrada / Teste de Execução
# ==========================================
if __name__ == "__main__":
    # Variáveis de ambiente ou parâmetros recebidos da sua API de geração (GPT/ElevenLabs)
    audio_source = "assets/wealthlogic_voiceover_en.mp3"
    
    # É fundamental garantir que todas as imagens possuam a proporção 16:9 (ex: 1920x1080)
    visual_assets = [
        "assets/scene_01_brain.jpg",
        "assets/scene_02_graph.jpg",
        "assets/scene_03_money.jpg"
    ]
    
    output_target = "out/wealthlogic_ep01_final.mp4"
    
    # Descomente a linha abaixo para executar assim que possuir os arquivos no diretório:
    # build_wealthlogic_video(audio_source, visual_assets, output_target)