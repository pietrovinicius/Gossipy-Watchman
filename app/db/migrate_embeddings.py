import os
import sys
import logging
from pathlib import Path
import cv2
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configurar logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate_embeddings")

# Adicionar a raiz do projeto ao path para conseguir importar app
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.core.settings import settings
from app.models.person import Person
from app.services.face_service import get_face_models

def pad_image(img: np.ndarray, pad_ratio: float = 0.3) -> np.ndarray:
    """Adiciona bordas ao redor do crop da face para ajudar o YuNet a detectar."""
    h, w = img.shape[:2]
    top = int(h * pad_ratio)
    bottom = int(h * pad_ratio)
    left = int(w * pad_ratio)
    right = int(w * pad_ratio)
    return cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_REPLICATE)

def migrate():
    logger.info("Iniciando migração de embeddings de face para YuNet + SFace...")
    
    # Criar sessão do banco
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()
    
    try:
        people = db.query(Person).all()
        logger.info(f"Encontradas {len(people)} pessoas no banco de dados.")
        
        success_count = 0
        fail_count = 0
        
        for person in people:
            person_id = person.id
            img_filename = f"{person_id}.jpg"
            img_path = settings.STORAGE_FACES / img_filename
            npy_path = settings.STORAGE_FACES / f"{person_id}.npy"
            
            if not img_path.exists():
                logger.warning(f"Pessoa ID {person_id} ({person.name}): Imagem {img_path} não encontrada em disco. Ignorando.")
                fail_count += 1
                continue
                
            img = cv2.imread(str(img_path))
            if img is None:
                logger.error(f"Pessoa ID {person_id} ({person.name}): Falha ao ler imagem {img_path}. Ignorando.")
                fail_count += 1
                continue
                
            # Tentar detectar na imagem bruta. Se falhar, tenta com padding.
            detected = False
            for pad in [0.0, 0.2, 0.4]:
                proc_img = pad_image(img, pad) if pad > 0.0 else img
                h, w = proc_img.shape[:2]
                
                # Instanciar modelos para a resolução da imagem
                # Usamos score_threshold baixo (0.1) no detector de migração para máxima sensibilidade
                detector = cv2.FaceDetectorYN.create(
                    model=str(Path(settings.STORAGE_FACES.parent / "models" / "face_detection_yunet_2023mar.onnx")),
                    config="",
                    input_size=(w, h),
                    score_threshold=0.1,
                    nms_threshold=0.3
                )
                
                _, recognizer = get_face_models((w, h))
                
                _, faces = detector.detect(proc_img)
                if faces is not None and len(faces) > 0:
                    # Usar a face de maior confiança detectada
                    best_face = max(faces, key=lambda f: f[14])
                    
                    try:
                        aligned = recognizer.alignCrop(proc_img, best_face)
                        feat = recognizer.feature(aligned)
                        embedding = feat.flatten().astype(np.float64)
                        
                        # Normalização L2
                        norm = np.linalg.norm(embedding)
                        if norm > 0:
                            embedding = embedding / norm
                            
                        # Salvar novo embedding
                        np.save(str(npy_path), embedding)
                        logger.info(f"Pessoa ID {person_id} ({person.name}): Novo embedding SFace gerado com sucesso (pad={pad}).")
                        success_count += 1
                        detected = True
                        break
                    except Exception as e:
                        logger.debug(f"Falha ao alinhar/extrair com pad={pad}: {e}")
            
            if not detected:
                logger.error(f"Pessoa ID {person_id} ({person.name}): YuNet não conseguiu encontrar rosto na imagem de referência. Não foi possível migrar.")
                fail_count += 1
                
        logger.info("Migração concluída!")
        logger.info(f"Migrados com sucesso: {success_count} perfis.")
        logger.info(f"Falhas/Ignorados: {fail_count} perfis.")
        
    except Exception as e:
        logger.exception(f"Erro fatal durante a migração: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
