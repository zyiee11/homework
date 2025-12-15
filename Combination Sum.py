#https://leetcode.com/problems/combination-sum/description/

def combinationSum(candidates, target):
    results = []
    
    def backtrack(remaining, combo, start):
        if remaining == 0:
            results.append(list(combo))
            return
        if remaining < 0:
            return
        
        for i in range(start, len(candidates)):
            combo.append(candidates[i])
            backtrack(remaining - candidates[i], combo, i)
            combo.pop()
    
    backtrack(target, [], 0)
    return results

print(combinationSum([2,3,6,7], 7))
# [[2, 2, 3], [7]]

print(combinationSum([2,3,5], 8))
# [[2, 2, 2, 2], [2, 3, 3], [3, 5]]

print(combinationSum([2], 1))
# []