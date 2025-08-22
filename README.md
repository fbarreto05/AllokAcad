# 🎓 AllokAcad

Descrição:  
AllokAcad é um sistema completo para atribuição de aulas em universidades, integrando front-end, back-end e dashboards analíticos.  
Permite organizar professores, turmas, componentes curriculares e salas, conciliando agendas e múltiplas restrições institucionais.  
O sistema segue a arquitetura MVT (Model-View-Template), garantindo separação entre dados, interface e controle, facilitando manutenção e escalabilidade.

---

## 💻 Front-end
- Tecnologias: HTML5, CSS3, JavaScript  
- Funcionalidades:  
  - Interfaces web intuitivas e interativas  
  - Adaptável a desktop, tablet e mobile  
  - Integração com back-end e dashboards  
- Uso de IA: 💡 otimização de prototipagem e sugestões de design  

---

## ⚙ Back-end
- Arquitetura: MVT (Model-View-Template)  
- Tecnologias: Python, Django, PostgreSQL  
- Funcionalidades:  
  - Gerenciamento de recursos como docentes, turmas, matérias e salas por meio de CRUD
  - Coleta de preferência dos docentes por meio de formulários  
  - Validação de regras institucionais e restrições de horários como critérios para o algoritmo  
  - Formação de atividades e grades horárias com base nas preferências, critérios e recursos do sistema
  - Uso de APIs para integração com front-end e dashboards
  
---

## 📊 Métricas / Dashboards
- *Tecnologias:* Python, Django, JavaScript, Chart.js  

### 🏗️ Arquitetura da Solução 
- ETL (Extract, Transform, Load):  
    - *Extract:* dados são extraídos das models de AllokAcads. 
    - *Transform & Load:* processados e carregados para as models de Dashboard.  
    - *Consulta & Visualização:* os dashboards acessam os dados da models de Dashboard para gerar gráficos.  

- ### Funcionalidades: 
    - Visualização de métricas de Professores e Espaços 
    - Gráficos interativos com Chart.js 
    - Atualização de dados por: acesso ao dashboard ou botão “Atualizar” 

### 🤖 Uso de IA
- Apoio no desenvolvimento dos gráficos em JavaScript com Chart.js
