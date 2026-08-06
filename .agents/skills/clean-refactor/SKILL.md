---
name: clean-refactor
description: Refactoriza funciones complejas o extensas dividiéndolas en módulos pequeños con responsabilidad única (SRP).
---

# Skill: Refactorización Modular (Clean Code & SRP)

**Contexto**: Esta skill se activa cuando el usuario o el agente solicitan refactorizar un bloque de código, función o módulo grande.

**Instrucciones a seguir:**

1. **Analizar Responsabilidades**:
   - Identifica cada tarea independiente dentro de la función original (ej. validación, formateo, cálculo, I/O).

2. **Extraer Sub-Funciones Puras**:
   - Crea funciones auxiliares pequeñas y reutilizables, preferiblemente con longitud < 25 líneas.
   - Aplica Type Hints completos a cada sub-función extraída.

3. **Preservar el Contrato Original**:
   - La función principal debe actuar únicamente como un orquestador de alto nivel fácil de leer.
   - No alterar la firma de entrada/salida a menos que sea explícitamente requerido.

4. **Verificación de Pruebas**:
   - Asegura que las pruebas unitarias existentes sigan pasando tras la refactorización.
