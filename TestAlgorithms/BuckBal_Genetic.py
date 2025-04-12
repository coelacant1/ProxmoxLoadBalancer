# Copyright (C) 2025 Coela Can't
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import random

class BucketBalancer:
    def __init__(self, buckets, population_size=100, generations=25, mutation_rate=0.1):
        self.buckets = buckets
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.tolerance = 0.05  # +/- 5% tolerance
        self.population = []

    def get_total_load(self):
        """Calculate the total load across all buckets."""
        return sum(bucket.get_total_load() for bucket in self.buckets)

    def target_load(self, bucket_capacity, total_capacity, total_load):
        """Calculate the target load for a bucket based on its capacity and total system load."""
        return (bucket_capacity / total_capacity) * total_load

    def is_within_tolerance(self, bucket_load, target_load):
        """Check if a bucket's load is within the +/- 5% tolerance."""
        return abs(bucket_load - target_load) <= target_load * self.tolerance

    def can_add_item(self, bucket, item):
        """Check if adding an item to the bucket will exceed its capacity."""
        return bucket.get_total_load() + item.load <= bucket.capacity

    def initialize_population(self):
        """Initialize a random population of item distributions based on current bucket items."""
        items = [item for bucket in self.buckets for item in bucket.items]  # Flatten all items in all buckets
        for _ in range(self.population_size):
            distribution = []
            for item in items:
                bucket = random.choice(self.buckets)
                while not self.can_add_item(bucket, item):
                    bucket = random.choice(self.buckets)  # Ensure the item can fit in the chosen bucket
                distribution.append(bucket)
            self.population.append(distribution)

    def fitness(self, distribution):
        """Evaluate the fitness of a distribution (how balanced the loads are)."""
        total_capacity = sum(bucket.capacity for bucket in self.buckets)
        total_load = self.get_total_load()
        targets = {bucket.id: self.target_load(bucket.capacity, total_capacity, total_load) for bucket in self.buckets}

        # Calculate the total imbalance across all buckets
        imbalance = 0
        for bucket in self.buckets:
            bucket_load = sum(item.load for item, assigned_bucket in zip([item for bucket in self.buckets for item in bucket.items], distribution) if assigned_bucket == bucket)
            if not self.is_within_tolerance(bucket_load, targets[bucket.id]):
                imbalance += abs(bucket_load - targets[bucket.id])

        return 1 / (1 + imbalance)  # Lower imbalance means better fitness

    def selection(self):
        """Select two parents based on fitness (higher fitness -> higher chance of selection)."""
        fitness_scores = [(self.fitness(chromosome), chromosome) for chromosome in self.population]
        fitness_scores.sort(reverse=True, key=lambda x: x[0])
        return random.choices(fitness_scores, weights=[score[0] for score in fitness_scores], k=2)

    def crossover(self, parent1, parent2):
        """Create offspring by crossover between two parents."""
        crossover_point = random.randint(0, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2

    def mutate(self, chromosome):
        """Randomly mutate a chromosome by changing the bucket of some items."""
        items = [item for bucket in self.buckets for item in bucket.items]  # Flatten all items
        for i, item in enumerate(items):
            if random.random() < self.mutation_rate:
                new_bucket = random.choice(self.buckets)
                while not self.can_add_item(new_bucket, item):  # Ensure the item can fit in the new bucket
                    new_bucket = random.choice(self.buckets)
                chromosome[i] = new_bucket

    def evolve(self):
        """Evolve the population over generations to find the best distribution."""
        self.initialize_population()

        i = 0
        for generation in range(self.generations):
            new_population = []

            i += 1

            print(i)
        
            # Selection and Crossover
            for _ in range(self.population_size // 2):
                parent1, parent2 = self.selection()
                child1, child2 = self.crossover(parent1[1], parent2[1])
                new_population.extend([child1, child2])

            # Mutation
            for chromosome in new_population:
                self.mutate(chromosome)

            self.population = new_population

        # Return the best solution
        best_solution = max(self.population, key=lambda x: self.fitness(x))
        return best_solution

    def apply_best_solution(self, best_solution):
        """Apply the best solution back to the actual bucket item distribution."""
        items = [item for bucket in self.buckets for item in bucket.items]
        for item, assigned_bucket in zip(items, best_solution):
            if item.bucket != assigned_bucket:
                item.bucket.remove_item(item)  # Remove item from the current bucket
                assigned_bucket.add_item(item)  # Add item to the new bucket
