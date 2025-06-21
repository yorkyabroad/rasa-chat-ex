# Debugging Guide

## Intent Recognition Issues

### Debug Intent Classification

1. **Interactive Learning Mode**
```bash
rasa interactive
```
This mode allows you to:
- Test conversations in real-time
- See confidence scores for intents
- Correct misclassified intents
- Add new training examples

2. **Intent Confidence Analysis**
```bash
rasa shell --debug
```
Look for:
- Low confidence scores (<0.7)
- Competing intents with similar scores
- Mismatched entities

3. **NLU Testing**
```bash
rasa test nlu --out results/nlu
```
Analyzes:
- Intent classification accuracy
- Entity extraction performance
- Confusion matrix for intents

### Common Intent Issues

1. **Similar Intents**
Problem: "ask_weather" and "ask_forecast" getting confused
Solution:
- Make training examples more distinct
- Consider combining similar intents
- Add discriminating features

2. **Missing Entities**
Problem: Location not being extracted
Solution:
- Add more entity examples
- Check entity format in training data
- Verify entity extractor configuration

## Story Debugging

### Debug Story Flows

1. **Interactive Story Creation**
```bash
rasa interactive
```
Benefits:
- Visualize conversation paths
- Identify missing story branches
- Test alternative responses

2. **Story Visualization**
```bash
rasa visualize
```
Shows:
- Story flow diagrams
- Decision points
- Action sequences

3. **Story Testing**
```bash
rasa test core --stories tests/test_stories.yml
```
Checks:
- Story completion rates
- Action prediction accuracy
- Failed conversation paths

### Common Story Issues

1. **Unexpected Actions**
Problem: Bot choosing wrong actions
Solution:
- Review policy configuration
- Check story coverage
- Add more training examples

2. **Stuck Conversations**
Problem: Bot not progressing in dialogue
Solution:
- Verify slot settings
- Check form configuration
- Review conversation flow logic

## Pipeline Refinement

### Pipeline Analysis

1. **Component Evaluation**
```yaml
pipeline:
  - name: WhitespaceTokenizer
    analyzer: word
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 4
  - name: DIETClassifier
    epochs: 100
    constrain_similarities: true
  - name: EntitySynonymMapper
  - name: ResponseSelector
    epochs: 100
    constrain_similarities: true
```

2. **Performance Metrics**
```bash
rasa test nlu --config config.yml
```
Analyzes:
- Processing time per component
- Memory usage
- Classification metrics

### Pipeline Optimization

1. **Feature Extraction**
- Adjust tokenization methods
- Try different featurizers
- Experiment with n-gram sizes

2. **Model Architecture**
- Tune DIET classifier parameters
- Adjust epoch numbers
- Modify layer sizes

3. **Custom Components**
```python
from rasa.nlu.components import Component

class CustomFeaturizer(Component):
    """Custom pipeline component for specific features"""
    
    def train(self, training_data, cfg, **kwargs):
        pass
        
    def process(self, message, **kwargs):
        pass
```

## Debugging Tools

### Rasa X/Enterprise
- Conversation review
- Interactive learning
- Performance monitoring

### Command Line Tools
```bash
# Debug specific conversations
rasa shell --debug

# Test specific intents
rasa shell nlu

# Evaluate model
rasa test

# Interactive debugging
rasa interactive
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

## Performance Monitoring

1. **Model Metrics**
- Intent classification accuracy
- Entity extraction F1-score
- Response selection precision

2. **System Metrics**
- Response time
- Memory usage
- API latency

3. **User Metrics**
- Conversation completion rate
- User satisfaction scores
- Fallback frequency