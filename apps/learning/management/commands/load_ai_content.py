"""
Management command to load sample AI learning content.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.learning.models import LearningPath, Module, Content
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Load sample AI learning content into the database'
    
    def handle(self, *args, **options):
        self.stdout.write('Loading AI learning content...')
        
        # Get or create admin user
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )
        
        # Create learning paths
        self.create_intro_to_ml_path(admin_user)
        self.create_nlp_path(admin_user)
        self.create_computer_vision_path(admin_user)
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded AI learning content!'))
    
    def create_intro_to_ml_path(self, user):
        """Create Introduction to Machine Learning path."""
        path, created = LearningPath.objects.get_or_create(
            slug='intro-to-machine-learning',
            defaults={
                'title': 'Introduction to Machine Learning',
                'description': 'Learn the fundamentals of machine learning, from basic concepts to practical applications. Perfect for beginners starting their AI journey.',
                'difficulty_level': 'beginner',
                'estimated_hours': 20,
                'tags': ['machine learning', 'AI', 'beginner', 'supervised learning', 'python'],
                'is_published': True,
                'created_by': user,
            }
        )
        
        if created:
            self.stdout.write(f'Created learning path: {path.title}')
            
            # Module 1: Introduction
            module1 = Module.objects.create(
                learning_path=path,
                title='What is Machine Learning?',
                description='Understanding the basics of machine learning and its applications',
                order=1,
                estimated_minutes=45
            )
            
            Content.objects.create(
                module=module1,
                title='Introduction to ML',
                content_type='text',
                order=1,
                text_content="""# Introduction to Machine Learning

Machine Learning (ML) is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. Instead of following pre-programmed rules, ML systems can identify patterns in data and make decisions or predictions based on those patterns.

## Key Concepts:

1. **Training Data**: The data used to teach the machine learning model
2. **Features**: The input variables used to make predictions
3. **Labels**: The output or target variable we want to predict
4. **Model**: The mathematical representation of patterns learned from data

## Types of Machine Learning:

- **Supervised Learning**: Learning from labeled data
- **Unsupervised Learning**: Finding patterns in unlabeled data
- **Reinforcement Learning**: Learning through trial and error

Machine learning powers many applications you use every day, from recommendation systems on Netflix to voice assistants like Siri and Alexa.""",
                estimated_minutes=15,
                difficulty='beginner'
            )
            
            Content.objects.create(
                module=module1,
                title='ML Applications',
                content_type='text',
                order=2,
                text_content="""# Real-World Machine Learning Applications

Machine learning is transforming industries across the globe. Here are some exciting applications:

## Healthcare
- Disease diagnosis from medical images
- Drug discovery and development
- Personalized treatment recommendations

## Finance
- Fraud detection
- Credit scoring
- Algorithmic trading

## E-commerce
- Product recommendations
- Price optimization
- Customer segmentation

## Transportation
- Self-driving cars
- Traffic prediction
- Route optimization

## Entertainment
- Content recommendation (Netflix, Spotify)
- Personalized advertising
- Gaming AI

Understanding these applications helps you see the practical value of learning ML.""",
                estimated_minutes=15,
                difficulty='beginner'
            )
            
            # Module 2: Python for ML
            module2 = Module.objects.create(
                learning_path=path,
                title='Python for Machine Learning',
                description='Essential Python libraries and tools for ML',
                order=2,
                estimated_minutes=90
            )
            
            Content.objects.create(
                module=module2,
                title='NumPy Basics',
                content_type='code',
                order=1,
                text_content='NumPy is the fundamental package for numerical computing in Python. It provides support for large, multi-dimensional arrays and matrices.',
                code_content="""import numpy as np

# Creating arrays
arr = np.array([1, 2, 3, 4, 5])
print("Array:", arr)

# Matrix operations
matrix = np.array([[1, 2], [3, 4]])
print("Matrix:\\n", matrix)

# Basic operations
print("Mean:", np.mean(arr))
print("Standard deviation:", np.std(arr))
print("Matrix transpose:\\n", matrix.T)

# Array indexing and slicing
print("First element:", arr[0])
print("Slice:", arr[1:4])""",
                estimated_minutes=30,
                difficulty='beginner'
            )
            
            # Module 3: Supervised Learning
            module3 = Module.objects.create(
                learning_path=path,
                title='Supervised Learning Basics',
                description='Understanding supervised learning algorithms',
                order=3,
                estimated_minutes=120
            )
            
            Content.objects.create(
                module=module3,
                title='Linear Regression',
                content_type='text',
                order=1,
                text_content="""# Linear Regression

Linear regression is one of the simplest and most widely used machine learning algorithms. It models the relationship between a dependent variable and one or more independent variables.

## How it Works:

The algorithm tries to find the best-fitting line through the data points. The line is represented by the equation:

y = mx + b

Where:
- y is the predicted value
- m is the slope
- x is the input feature
- b is the y-intercept

## Use Cases:

- Predicting house prices based on size
- Forecasting sales based on advertising spend
- Estimating salary based on years of experience

## Key Concepts:

1. **Loss Function**: Measures how far predictions are from actual values
2. **Gradient Descent**: Algorithm to minimize the loss function
3. **R-squared**: Metric to evaluate model performance""",
                estimated_minutes=30,
                difficulty='beginner'
            )
    
    def create_nlp_path(self, user):
        """Create NLP Fundamentals path."""
        path, created = LearningPath.objects.get_or_create(
            slug='nlp-fundamentals',
            defaults={
                'title': 'Natural Language Processing Fundamentals',
                'description': 'Master the basics of NLP and learn how to build applications that understand and generate human language.',
                'difficulty_level': 'intermediate',
                'estimated_hours': 25,
                'tags': ['NLP', 'text analysis', 'transformers', 'deep learning'],
                'is_published': True,
                'created_by': user,
            }
        )
        
        if created:
            self.stdout.write(f'Created learning path: {path.title}')
            
            module1 = Module.objects.create(
                learning_path=path,
                title='Introduction to NLP',
                description='Understanding natural language processing concepts',
                order=1,
                estimated_minutes=60
            )
            
            Content.objects.create(
                module=module1,
                title='What is NLP?',
                content_type='text',
                order=1,
                text_content="""# Natural Language Processing

Natural Language Processing (NLP) is a branch of AI that helps computers understand, interpret, and generate human language. It bridges the gap between human communication and computer understanding.

## Key NLP Tasks:

1. **Text Classification**: Categorizing text into predefined classes
2. **Named Entity Recognition**: Identifying entities like names, locations, dates
3. **Sentiment Analysis**: Determining the emotional tone of text
4. **Machine Translation**: Translating text from one language to another
5. **Question Answering**: Building systems that can answer questions
6. **Text Generation**: Creating human-like text

## Modern NLP:

Today's NLP is powered by deep learning models like:
- Transformers (BERT, GPT)
- Recurrent Neural Networks
- Attention mechanisms

These models have revolutionized how machines understand language.""",
                estimated_minutes=20,
                difficulty='intermediate'
            )
    
    def create_computer_vision_path(self, user):
        """Create Computer Vision path."""
        path, created = LearningPath.objects.get_or_create(
            slug='computer-vision-basics',
            defaults={
                'title': 'Computer Vision Basics',
                'description': 'Learn how to build AI systems that can see and understand visual information from the world.',
                'difficulty_level': 'intermediate',
                'estimated_hours': 30,
                'tags': ['computer vision', 'CNN', 'image processing', 'deep learning'],
                'is_published': True,
                'created_by': user,
            }
        )
        
        if created:
            self.stdout.write(f'Created learning path: {path.title}')
            
            module1 = Module.objects.create(
                learning_path=path,
                title='Introduction to Computer Vision',
                description='Understanding how computers see',
                order=1,
                estimated_minutes=75
            )
            
            Content.objects.create(
                module=module1,
                title='Computer Vision Overview',
                content_type='text',
                order=1,
                text_content="""# Computer Vision

Computer Vision is a field of AI that trains computers to interpret and understand the visual world. Using digital images and deep learning models, machines can accurately identify and classify objects, and react to what they "see."

## Applications:

1. **Image Classification**: Identifying what's in an image
2. **Object Detection**: Finding and locating objects in images
3. **Semantic Segmentation**: Classifying each pixel in an image
4. **Facial Recognition**: Identifying individuals from their faces
5. **Optical Character Recognition**: Reading text from images
6. **Medical Image Analysis**: Detecting diseases from X-rays, MRIs

## Key Technologies:

- Convolutional Neural Networks (CNNs)
- Transfer Learning
- Data Augmentation
- Pre-trained Models (ResNet, VGG, YOLO)

Computer vision is one of the most exciting and rapidly advancing fields in AI.""",
                estimated_minutes=25,
                difficulty='intermediate'
            )

