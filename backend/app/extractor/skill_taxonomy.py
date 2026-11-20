"""Comprehensive tech skill taxonomy with canonical names, categories, and synonym mapping."""

SKILL_TAXONOMY = {
    # Programming Languages
    "python": {"canonical": "Python", "category": "Languages", "aliases": ["python3", "py3", "python 3"]},
    "java": {"canonical": "Java", "category": "Languages", "aliases": ["core java", "java 8", "java 11", "java 17", "java 21"]},
    "javascript": {"canonical": "JavaScript", "category": "Languages", "aliases": ["js", "es6", "es2020", "vanilla js"]},
    "typescript": {"canonical": "TypeScript", "category": "Languages", "aliases": ["ts"]},
    "c++": {"canonical": "C++", "category": "Languages", "aliases": ["cpp", "c plus plus"]},
    "c#": {"canonical": "C#", "category": "Languages", "aliases": ["csharp", "c sharp", ".net c#"]},
    "golang": {"canonical": "Go", "category": "Languages", "aliases": ["go lang", "golang", "go language"]},
    "rust": {"canonical": "Rust", "category": "Languages", "aliases": ["rust-lang"]},
    "ruby": {"canonical": "Ruby", "category": "Languages", "aliases": ["ruby on rails"]},
    "php": {"canonical": "PHP", "category": "Languages", "aliases": ["php7", "php8"]},
    "swift": {"canonical": "Swift", "category": "Languages", "aliases": ["swiftui", "ios swift"]},
    "kotlin": {"canonical": "Kotlin", "category": "Languages", "aliases": ["android kotlin"]},
    "sql": {"canonical": "SQL", "category": "Languages", "aliases": ["structured query language", "t-sql", "plsql", "pl/sql", "ansi sql"]},
    "bash": {"canonical": "Bash", "category": "Languages", "aliases": ["shell", "shell scripting", "sh", "zsh"]},
    "html": {"canonical": "HTML5", "category": "Frontend", "aliases": ["html", "html5"]},
    "css": {"canonical": "CSS3", "category": "Frontend", "aliases": ["css", "css3", "sass", "scss", "less"]},

    # Frontend Frameworks & Libraries
    "react": {"canonical": "React", "category": "Frontend", "aliases": ["react.js", "reactjs", "react js"]},
    "angular": {"canonical": "Angular", "category": "Frontend", "aliases": ["angular.js", "angularjs", "angular 2+"]},
    "vue": {"canonical": "Vue.js", "category": "Frontend", "aliases": ["vue.js", "vuejs", "vue 3", "vue"]},
    "next.js": {"canonical": "Next.js", "category": "Frontend", "aliases": ["nextjs", "next js", "next"]},
    "svelte": {"canonical": "Svelte", "category": "Frontend", "aliases": ["sveltekit"]},
    "redux": {"canonical": "Redux", "category": "Frontend", "aliases": ["redux toolkit", "rtk"]},
    "tailwind": {"canonical": "Tailwind CSS", "category": "Frontend", "aliases": ["tailwind", "tailwindcss", "tailwind-css"]},
    "bootstrap": {"canonical": "Bootstrap", "category": "Frontend", "aliases": ["bootstrap 5", "twitter bootstrap"]},

    # Backend & Frameworks
    "fastapi": {"canonical": "FastAPI", "category": "Backend", "aliases": ["fast api", "fastapi framework"]},
    "django": {"canonical": "Django", "category": "Backend", "aliases": ["django rest framework", "drf"]},
    "flask": {"canonical": "Flask", "category": "Backend", "aliases": ["flask framework"]},
    "spring boot": {"canonical": "Spring Boot", "category": "Backend", "aliases": ["springboot", "spring-boot", "spring framework", "spring"]},
    "node.js": {"canonical": "Node.js", "category": "Backend", "aliases": ["nodejs", "node js", "node"]},
    "express": {"canonical": "Express.js", "category": "Backend", "aliases": ["express", "expressjs", "express.js"]},
    "nest.js": {"canonical": "NestJS", "category": "Backend", "aliases": ["nestjs", "nest js"]},
    "asp.net": {"canonical": "ASP.NET", "category": "Backend", "aliases": ["asp.net core", ".net core", "dotnet", "dotnet core"]},
    "graphql": {"canonical": "GraphQL", "category": "Backend", "aliases": ["apollo graphql"]},
    "rest apis": {"canonical": "REST APIs", "category": "Backend", "aliases": ["rest", "rest api", "restful", "restful api", "restful apis", "rest-api", "web apis"]},
    "microservices": {"canonical": "Microservices", "category": "Architecture", "aliases": ["microservice", "microservice architecture", "distributed services"]},
    "system design": {"canonical": "System Design", "category": "Architecture", "aliases": ["distributed systems", "software architecture", "high availability"]},

    # Databases & Caching
    "postgresql": {"canonical": "PostgreSQL", "category": "Databases", "aliases": ["postgres", "pgsql", "postgre sql"]},
    "mysql": {"canonical": "MySQL", "category": "Databases", "aliases": ["my-sql"]},
    "mongodb": {"canonical": "MongoDB", "category": "Databases", "aliases": ["mongo", "nosql mongodb"]},
    "redis": {"canonical": "Redis", "category": "Databases", "aliases": ["redis cache"]},
    "elasticsearch": {"canonical": "Elasticsearch", "category": "Databases", "aliases": ["elastic search", "elk", "opensearch"]},
    "cassandra": {"canonical": "Cassandra", "category": "Databases", "aliases": ["apache cassandra"]},
    "dynamodb": {"canonical": "DynamoDB", "category": "Databases", "aliases": ["aws dynamodb", "dynamo db"]},
    "sqlite": {"canonical": "SQLite", "category": "Databases", "aliases": ["sqlite3"]},

    # Cloud & DevOps
    "aws": {"canonical": "AWS", "category": "Cloud & DevOps", "aliases": ["amazon web services", "aws ec2", "aws s3", "aws lambda", "aws cloud"]},
    "azure": {"canonical": "Azure", "category": "Cloud & DevOps", "aliases": ["microsoft azure", "azure cloud", "azure devops"]},
    "gcp": {"canonical": "GCP", "category": "Cloud & DevOps", "aliases": ["google cloud", "google cloud platform"]},
    "docker": {"canonical": "Docker", "category": "Cloud & DevOps", "aliases": ["docker containers", "containerization"]},
    "kubernetes": {"canonical": "Kubernetes", "category": "Cloud & DevOps", "aliases": ["k8s", "kube"]},
    "ci/cd": {"canonical": "CI/CD", "category": "Cloud & DevOps", "aliases": ["cicd", "continuous integration", "continuous deployment", "jenkins", "github actions", "gitlab ci"]},
    "terraform": {"canonical": "Terraform", "category": "Cloud & DevOps", "aliases": ["tf", "infrastructure as code", "iac"]},
    "linux": {"canonical": "Linux", "category": "Cloud & DevOps", "aliases": ["ubuntu", "debian", "centos", "redhat", "unix"]},
    "git": {"canonical": "Git", "category": "Cloud & DevOps", "aliases": ["github", "gitlab", "bitbucket", "version control"]},

    # AI / Machine Learning / NLP
    "machine learning": {"canonical": "Machine Learning", "category": "AI / ML", "aliases": ["ml", "machine-learning", "machine learning algorithms"]},
    "deep learning": {"canonical": "Deep Learning", "category": "AI / ML", "aliases": ["dl", "deep-learning", "neural networks", "ann", "rnn"]},
    "cnn": {"canonical": "CNN", "category": "AI / ML", "aliases": ["convolutional neural networks", "convolutional neural network", "convnet", "convnets", "cnns"]},
    "nlp": {"canonical": "NLP", "category": "AI / ML", "aliases": ["natural language processing", "text analytics", "computational linguistics", "text preprocessing"]},
    "computer vision": {"canonical": "Computer Vision", "category": "AI / ML", "aliases": ["cv", "opencv", "image processing", "object detection"]},
    "spacy": {"canonical": "spaCy", "category": "AI / ML", "aliases": ["spacy nlp"]},
    "sentence transformers": {"canonical": "Sentence Transformers", "category": "AI / ML", "aliases": ["sentence-transformers", "sbert", "sentence embeddings"]},
    "pytorch": {"canonical": "PyTorch", "category": "AI / ML", "aliases": ["torch", "pytorch framework"]},
    "tensorflow": {"canonical": "TensorFlow", "category": "AI / ML", "aliases": ["tf", "keras", "tensorflow 2", "tf.keras"]},
    "scikit-learn": {"canonical": "Scikit-Learn", "category": "AI / ML", "aliases": ["sklearn", "scikit learn", "scikit"]},
    "huggingface": {"canonical": "Hugging Face", "category": "AI / ML", "aliases": ["hugging face", "transformers", "hf", "huggingface transformers"]},
    "generative ai": {"canonical": "Generative AI", "category": "AI / ML", "aliases": ["genai", "gen-ai", "generative-ai"]},
    "large language models": {"canonical": "LLMs", "category": "AI / ML", "aliases": ["llm", "llms", "large language model", "large language models"]},
    "rag": {"canonical": "RAG", "category": "AI / ML", "aliases": ["retrieval augmented generation", "retrieval-augmented generation", "rag pipeline"]},
    "prompt engineering": {"canonical": "Prompt Engineering", "category": "AI / ML", "aliases": ["prompt design", "few-shot prompting", "chain-of-thought"]},
    "langchain": {"canonical": "LangChain", "category": "AI / ML", "aliases": ["lang-chain", "llamaindex", "llama-index"]},
    "pandas": {"canonical": "Pandas", "category": "AI / ML", "aliases": ["pandas dataframe"]},
    "numpy": {"canonical": "NumPy", "category": "AI / ML", "aliases": ["numpy array"]},

    # Testing & Methodologies
    "unit testing": {"canonical": "Unit Testing", "category": "Testing", "aliases": ["pytest", "jest", "junit", "test driven development", "tdd", "integration testing"]},
    "agile": {"canonical": "Agile", "category": "Methodologies", "aliases": ["scrum", "kanban", "sprint planning"]},
    "problem solving": {"canonical": "Problem Solving", "category": "Soft Skills", "aliases": ["analytical thinking", "critical thinking"]},
}

# Inverted index: alias_lower -> canonical_name
ALIAS_MAP = {}
for key, data in SKILL_TAXONOMY.items():
    canonical = data["canonical"]
    ALIAS_MAP[key.lower()] = canonical
    ALIAS_MAP[canonical.lower()] = canonical
    for alias in data.get("aliases", []):
        ALIAS_MAP[alias.lower()] = canonical

def get_canonical_skill(skill_str: str) -> str:
    """Return the normalized canonical skill name or the title-cased string if unknown."""
    cleaned = skill_str.strip().lower()
    return ALIAS_MAP.get(cleaned, skill_str.strip().title())

AI_ML_CORE_SKILLS = {
    "Python", "PyTorch", "TensorFlow", "Scikit-Learn", "CNN", "NLP",
    "Machine Learning", "Deep Learning", "NumPy", "Pandas", "Computer Vision",
    "spaCy", "Sentence Transformers", "Hugging Face"
}

GENAI_CORE_SKILLS = {
    "Generative AI", "LLMs", "RAG", "Prompt Engineering", "LangChain",
    "Hugging Face", "Sentence Transformers"
}

TOOLS_DEPLOYMENT_CORE_SKILLS = {
    "FastAPI", "Flask", "Docker", "Kubernetes", "REST APIs", "CI/CD",
    "Git", "AWS", "Azure", "GCP", "Linux", "PostgreSQL", "MySQL",
    "MongoDB", "Redis", "Elasticsearch"
}
