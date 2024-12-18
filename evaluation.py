import time
from typing import Tuple

import pandas as pd

from txtagents import MinervaTeam
from typing import List, Dict
import logging

from tools import DatabaseConnector

class MinervaEvaluator:
    def __init__(self):
        self.agents = MinervaTeam()
        self.db_connector = DatabaseConnector()
   
        self.logger = logging.getLogger(__name__ + '.MinervaEvaluator')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
    
    async def predict(self, msg: str) -> Tuple[str, float]:
        """
        Analyze a text message and return the prediction.
        """
        start_time = time.perf_counter()
        try:
            stream = await self.agents.analyze_msg(msg)
            
            streams = []
            async for s in stream:
                streams.append(s)
            
            if streams and streams[-1] and streams[-1].messages:
                prediction = streams[-1].messages[-1].content
            else:
                prediction = "unknown,unknown,0.0"
            
            await self.agents.reset()
            latency = time.perf_counter() - start_time

            return prediction, latency
            
        except Exception as e:
            self.logger.error(f"Error during prediction: {e}")
            latency = time.perf_counter() - start_time

            return "error,unknown,0.0", latency

    async def evaluate_dataset(self, df_evals: pd.DataFrame) -> Dict:
        """
        Evaluate the model on a dataset and calculate metrics.
        """
        # run evals predictions
        latencies = []
        for i, row in df_evals.iterrows():
            self.logger.info(f"{row['category']}.{row['subcategory']}#{i}") 
            result, latency = await self.predict(row['message'])
            latencies.append(latency)

        # reverse preds order, and reset index
        df_preds = self.db_connector.get_top_k(i+1)
        df_preds = df_preds[::-1].reset_index(drop=True)

        # calculate metrics
        metrics = self.calculate_metrics(df_evals, df_preds)
        
        return {
            "metrics": metrics,
            "predictions": df_preds,
            "latency": sum(latencies) / len(latencies) 
        }
    
    def calculate_metrics(self, df_evals: pd.DataFrame, df_preds: pd.DataFrame) -> Dict:
        """
        Calculate evaluation metrics.
        """
        k = len(df_preds)
        df_evals = df_evals.head(k)

        correct = sum(df_evals['is_scam'] == df_preds['is_scam'])
        accuracy = correct / k if k > 0 else 0
        
        df_preds['confidence_level'] = df_preds['confidence_level'].astype(int)
        avg_confidence = df_preds['confidence_level'].mean()
        
        return {
            "accuracy": accuracy,
            "correct_predictions": correct,
            "total_samples": k,
            "average_confidence": avg_confidence
        }

async def main():
    evaluator = MinervaEvaluator()

    try:
        df_evals = pd.read_csv("./evals/commerce.csv")
        if not all(col in df_evals.columns for col in ['message', 'category', 'subcategory', 'is_scam']):
            raise ValueError("Required columns missing in evaluation dataset")
    
    except Exception as e:
        logging.error(f"Error loading dataset: {e}")

    results = await evaluator.evaluate_dataset(df_evals)
    
    print("\nEvaluation Results:")
    print(f"Accuracy: {results['metrics']['accuracy']:.2%}")
    print(f"Correct Predictions: {results['metrics']['correct_predictions']}/{results['metrics']['total_samples']}")
    print(f"Average Confidence: {results['metrics']['average_confidence']:.2}")
    print(f"Average Latency: {results['latency']:.1f} seconds")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())