"""
Configurações específicas do TensorFlow para otimização no Cloud Run
"""

import os
import logging

logger = logging.getLogger(__name__)

def configure_tensorflow_for_cloud_run():
    """
    Configura TensorFlow para otimizar performance no Cloud Run
    """
    try:
        # Configurar variáveis de ambiente antes de importar TensorFlow
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduzir logs verbosos
        os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Desabilitar otimizações oneAPI
        os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
        
        # Configurações para CPU
        os.environ['OMP_NUM_THREADS'] = '2'  # Limitar threads OpenMP
        os.environ['TF_NUM_INTEROP_THREADS'] = '2'
        os.environ['TF_NUM_INTRAOP_THREADS'] = '2'
        
        # Configurações de memória
        os.environ['TF_GPU_ALLOCATOR'] = 'cuda_malloc_async'
        
        # Importar TensorFlow após configurar variáveis
        import tensorflow as tf
        
        # Configurar threading
        tf.config.threading.set_inter_op_parallelism_threads(2)
        tf.config.threading.set_intra_op_parallelism_threads(2)
        
        # Configurar GPU se disponível (improvável no Cloud Run, mas por segurança)
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logger.info(f"Configured {len(gpus)} GPU(s) with memory growth")
            except RuntimeError as e:
                logger.warning(f"GPU configuration failed: {e}")
        
        # Configurar CPU para otimização
        cpus = tf.config.experimental.list_physical_devices('CPU')
        if cpus:
            logger.info(f"Found {len(cpus)} CPU(s)")
        
        # Configurações de otimização
        tf.config.optimizer.set_jit(True)  # Habilitar XLA JIT
        
        logger.info("TensorFlow configured for Cloud Run")
        return True
        
    except Exception as e:
        logger.error(f"Failed to configure TensorFlow: {e}")
        return False

def get_tensorflow_info():
    """
    Retorna informações sobre a configuração do TensorFlow
    """
    try:
        import tensorflow as tf
        
        info = {
            "tensorflow_version": tf.__version__,
            "gpu_available": len(tf.config.experimental.list_physical_devices('GPU')) > 0,
            "cpu_count": len(tf.config.experimental.list_physical_devices('CPU')),
            "mixed_precision": tf.keras.mixed_precision.global_policy().name,
            "xla_enabled": tf.config.optimizer.get_jit() is not None
        }
        
        return info
        
    except Exception as e:
        logger.error(f"Failed to get TensorFlow info: {e}")
        return {"error": str(e)}

def optimize_model_for_inference(model):
    """
    Otimiza modelo para inferência
    """
    try:
        import tensorflow as tf
        
        # Converter para TensorFlow Lite se possível (para modelos menores)
        # Nota: Isso pode não funcionar para todos os modelos
        
        # Por enquanto, apenas configurar para modo de inferência
        if hasattr(model, 'trainable'):
            model.trainable = False
        
        logger.info("Model optimized for inference")
        return model
        
    except Exception as e:
        logger.warning(f"Model optimization failed: {e}")
        return model

# Configurar TensorFlow na importação do módulo
configure_tensorflow_for_cloud_run()
