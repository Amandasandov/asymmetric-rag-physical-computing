# ==============================================================================
# ANÁLISIS DE RÚBRICAS: MODELO MIXTO ORDINAL (CLMM) a 2 Niveles
# ==============================================================================

while(sink.number() > 0) { sink() }

suppressPackageStartupMessages({
  library(ordinal)
  library(tidyr)
  library(dplyr)
  library(readxl)
})

archivo_excel <- "data/03_processed_metrics/Activities_evaluation_results.xlsx"
archivo_salida <- "CLMM_Rubric_Results.txt"

file.create(archivo_salida)

escribir <- function(texto) {
  cat(texto, "\n") 
  cat(texto, "\n", file = archivo_salida, append = TRUE) 
}

if (!file.exists(archivo_excel)) {
  escribir(sprintf("❌ ERROR: No se encuentra el archivo '%s'.", archivo_excel))
  stop("Ejecución detenida.")
}

df <- read_excel(archivo_excel)

df_long <- df %>%
  pivot_longer(
    cols = 4:11,
    names_to = "Subitem", 
    values_to = "Puntaje"
  ) %>%
  mutate(Dimension = sub(" \\(.*\\)", "", Subitem))

df_long$Modalidad <- factor(df_long$Modalidad)
df_long$Modalidad <- relevel(df_long$Modalidad, ref = "Humano")
df_long$Evaluador_ID <- as.factor(df_long$Evaluador_ID)
df_long$Actividad <- as.factor(df_long$Actividad)
df_long$Puntaje <- ordered(df_long$Puntaje) 

subitems <- unique(df_long$Subitem)
dimensiones <- unique(df_long$Dimension)

escribir("======================================================================")
escribir("MODELO MIXTO ORDINAL (CLMM) - NIVEL 1: 8 SUB-ÍTEMS")
escribir("======================================================================")

for(item in subitems) {
  datos_sub <- df_long %>% filter(Subitem == item)
  escribir(sprintf("\n---> SUB-ÍTEM: %s <---", item))
  
  resultado_modelo <- tryCatch({
    clmm(Puntaje ~ Modalidad + (1|Evaluador_ID) + (1|Actividad), data = datos_sub)
  }, error = function(e) { return(e) })
  
  if(inherits(resultado_modelo, "error")) {
    escribir(sprintf("   [!] ERROR: %s", resultado_modelo$message))
    next 
  }
  
  coefs <- summary(resultado_modelo)$coefficients
  filas_mod <- grep("Modalidad", rownames(coefs))
  ic <- suppressMessages(confint(resultado_modelo))
  
  for(i in filas_mod) {
    termino <- rownames(coefs)[i]
    estimacion <- coefs[i, "Estimate"]
    p_val <- coefs[i, "Pr(>|z|)"]
    or <- exp(estimacion) 
    
    idx_ic <- which(rownames(ic) == termino)
    if(length(idx_ic) > 0) {
      escribir(sprintf("   %s:\n      OR = %.2f [IC 95%%: %.2f - %.2f] | p-valor = %.4f", 
                       termino, or, exp(ic[idx_ic, 1]), exp(ic[idx_ic, 2]), p_val))
    } else {
      escribir(sprintf("   %s:\n      OR = %.2f (IC no disp.) | p-valor = %.4f", termino, or, p_val))
    }
  }
}

escribir("\n======================================================================")
escribir("MODELO MIXTO ORDINAL (CLMM) - NIVEL 2: 4 DIMENSIONES (Datos Apilados)")
escribir("======================================================================")

for(dim in dimensiones) {
  datos_sub <- df_long %>% filter(Dimension == dim)
  escribir(sprintf("\n---> DIMENSIÓN: %s <---", dim))
  
  resultado_modelo <- tryCatch({
    # Al filtrar por Dimensión, el modelo ahora incorpora los dos sub-ítems juntos
    clmm(Puntaje ~ Modalidad + (1|Evaluador_ID) + (1|Actividad), data = datos_sub)
  }, error = function(e) { return(e) })
  
  if(inherits(resultado_modelo, "error")) {
    escribir(sprintf("   [!] ERROR: %s", resultado_modelo$message))
    next 
  }
  
  coefs <- summary(resultado_modelo)$coefficients
  filas_mod <- grep("Modalidad", rownames(coefs))
  ic <- suppressMessages(confint(resultado_modelo))
  
  for(i in filas_mod) {
    termino <- rownames(coefs)[i]
    estimacion <- coefs[i, "Estimate"]
    p_val <- coefs[i, "Pr(>|z|)"]
    or <- exp(estimacion) 
    
    idx_ic <- which(rownames(ic) == termino)
    if(length(idx_ic) > 0) {
      escribir(sprintf("   %s:\n      OR = %.2f [IC 95%%: %.2f - %.2f] | p-valor = %.4f", 
                       termino, or, exp(ic[idx_ic, 1]), exp(ic[idx_ic, 2]), p_val))
    }
  }
}

escribir("\n======================================================================")
escribir(sprintf("✅ Análisis completado. Resultados en '%s'", archivo_salida))