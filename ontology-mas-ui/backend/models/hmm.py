"""HMM wrapper for hidden state inference via Viterbi."""
from typing import List, Tuple, Optional
import numpy as np  # type: ignore[import-not-found]
import logging

logger = logging.getLogger(__name__)

# Try to import hmmlearn, fallback to manual Viterbi
try:
    from hmmlearn import hmm as hmmlearn_hmm  # type: ignore[import-not-found]
    HAS_HMMLEARN = True
except ImportError:
    HAS_HMMLEARN = False
    logger.warning("hmmlearn not available, using manual Viterbi")

class HMMInference:
    """Discrete HMM for customer state inference."""
    
    def __init__(self, config: dict):
        """Initialize HMM from config.
        
        Args:
            config: {
                "states": ["Happy", "Neutral", "Unhappy"],
                "observations": ["Purchase", "Complaint", "Silence"],
                "start": [0.5, 0.3, 0.2],
                "transition": [[...], [...], [...]],
                "emission": [[...], [...], [...]]
            }
        """
        self.states = config["states"]
        self.observations = config["observations"]
        self.start_prob = np.array(config["start"])
        self.trans_matrix = np.array(config["transition"])
        self.emission_matrix = np.array(config["emission"])
        
        self.n_states = len(self.states)
        self.n_obs = len(self.observations)
        
        # Validate
        self._validate()
        
        # Build index maps
        self.state_to_idx = {s: i for i, s in enumerate(self.states)}
        self.obs_to_idx = {o: i for i, o in enumerate(self.observations)}
        
        # Initialize hmmlearn model if available
        if HAS_HMMLEARN:
            self.model = hmmlearn_hmm.CategoricalHMM(n_components=self.n_states)
            self.model.startprob_ = self.start_prob
            self.model.transmat_ = self.trans_matrix
            self.model.emissionprob_ = self.emission_matrix
    
    def _validate(self):
        """Validate probability matrices."""
        assert abs(self.start_prob.sum() - 1.0) < 1e-6, "Start probs must sum to 1"
        assert np.allclose(self.trans_matrix.sum(axis=1), 1.0), "Transition rows must sum to 1"
        assert np.allclose(self.emission_matrix.sum(axis=1), 1.0), "Emission rows must sum to 1"
    
    def viterbi(self, obs_sequence: List[str]) -> Tuple[List[str], float]:
        """Run Viterbi to infer most likely state sequence.
        
        Returns:
            (state_sequence, log_probability)
        """
        if not obs_sequence:
            return [], 0.0
        
        # Convert observations to indices
        try:
            obs_indices = [self.obs_to_idx[o] for o in obs_sequence]
        except KeyError as e:
            logger.error(f"Unknown observation: {e}")
            return [], float('-inf')
        
        if HAS_HMMLEARN:
            return self._viterbi_hmmlearn(obs_indices)
        else:
            return self._viterbi_manual(obs_indices)
    
    def _viterbi_hmmlearn(self, obs_indices: List[int]) -> Tuple[List[str], float]:
        """Use hmmlearn for Viterbi."""
        obs_array = np.array(obs_indices).reshape(-1, 1)
        logprob, state_seq = self.model.decode(obs_array, algorithm="viterbi")
        
        state_names = [self.states[i] for i in state_seq]
        return state_names, float(logprob)
    
    def _viterbi_manual(self, obs_indices: List[int]) -> Tuple[List[str], float]:
        """Manual Viterbi implementation."""
        T = len(obs_indices)
        
        # Initialize
        viterbi_matrix = np.zeros((self.n_states, T))
        backpointer = np.zeros((self.n_states, T), dtype=int)
        
        # First observation
        for s in range(self.n_states):
            viterbi_matrix[s, 0] = np.log(self.start_prob[s]) + \
                                    np.log(self.emission_matrix[s, obs_indices[0]])
        
        # Forward pass
        for t in range(1, T):
            for s in range(self.n_states):
                trans_probs = viterbi_matrix[:, t-1] + np.log(self.trans_matrix[:, s])
                backpointer[s, t] = np.argmax(trans_probs)
                viterbi_matrix[s, t] = trans_probs[backpointer[s, t]] + \
                                       np.log(self.emission_matrix[s, obs_indices[t]])
        
        # Backtrack
        best_path = np.zeros(T, dtype=int)
        best_path[-1] = np.argmax(viterbi_matrix[:, -1])
        
        for t in range(T-2, -1, -1):
            best_path[t] = backpointer[best_path[t+1], t+1]
        
        state_names = [self.states[i] for i in best_path]
        logprob = float(viterbi_matrix[best_path[-1], -1])
        
        return state_names, logprob
    
    def sample_observation(self, state: str) -> str:
        """Sample an observation given a state."""
        state_idx = self.state_to_idx[state]
        obs_probs = self.emission_matrix[state_idx]
        obs_idx = np.random.choice(self.n_obs, p=obs_probs)
        return self.observations[obs_idx]
    
    def sample_next_state(self, current_state: str) -> str:
        """Sample next state given current state."""
        state_idx = self.state_to_idx[current_state]
        trans_probs = self.trans_matrix[state_idx]
        next_idx = np.random.choice(self.n_states, p=trans_probs)
        return self.states[next_idx]
