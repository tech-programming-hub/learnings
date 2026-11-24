# 14 — Most-Asked Coding Questions (with Solutions)

> Curated from the most frequently asked coding-round questions for Java/Full-Stack roles (LeetCode "top interview" + company-repeated sets). Java-first with Python where useful. For each: know the **pattern**, the **complexity**, and the **edge cases**. Practice writing 5–6 of these from memory.
> Approach every problem: **Clarify → examples/edge cases → brute force → optimize (state Big-O) → code → test → discuss trade-offs. Think out loud.**

---

## A. Arrays & Hashing (most common category)

### 1. Two Sum — find indices of two numbers adding to target
```java
int[] twoSum(int[] a, int target) {
    Map<Integer,Integer> seen = new HashMap<>();
    for (int i = 0; i < a.length; i++) {
        int need = target - a[i];
        if (seen.containsKey(need)) return new int[]{seen.get(need), i};
        seen.put(a[i], i);
    }
    return new int[]{-1,-1};
}
```
**Pattern:** hashmap complement. **O(n) time, O(n) space.** Edge: no solution, duplicates.

### 2. Best Time to Buy and Sell Stock — max profit, buy before sell
```java
int maxProfit(int[] p) {
    int minPrice = Integer.MAX_VALUE, best = 0;
    for (int price : p) {
        minPrice = Math.min(minPrice, price);
        best = Math.max(best, price - minPrice);
    }
    return best;
}
```
**Pattern:** track running minimum. **O(n).** Edge: prices only decreasing → profit 0.

### 3. Contains Duplicate
```java
boolean containsDuplicate(int[] a) {
    Set<Integer> seen = new HashSet<>();
    for (int x : a) if (!seen.add(x)) return true;  // add returns false if already present
    return false;
}
```
**O(n).**

### 4. Maximum Subarray (Kadane's algorithm)
```java
int maxSubArray(int[] a) {
    int cur = a[0], best = a[0];
    for (int i = 1; i < a.length; i++) {
        cur = Math.max(a[i], cur + a[i]);   // extend or restart
        best = Math.max(best, cur);
    }
    return best;
}
```
**Pattern:** DP / running sum. **O(n).** Edge: all negatives (answer is the largest single element).

### 5. Product of Array Except Self (no division)
```java
int[] productExceptSelf(int[] a) {
    int n = a.length; int[] res = new int[n];
    res[0] = 1;
    for (int i = 1; i < n; i++) res[i] = res[i-1] * a[i-1];   // prefix products
    int right = 1;
    for (int i = n-1; i >= 0; i--) { res[i] *= right; right *= a[i]; } // suffix
    return res;
}
```
**Pattern:** prefix/suffix products. **O(n), O(1) extra** (besides output).

### 6. Move Zeroes to end (in place, keep order)
```java
void moveZeroes(int[] a) {
    int insert = 0;
    for (int x : a) if (x != 0) a[insert++] = x;
    while (insert < a.length) a[insert++] = 0;
}
```
**Pattern:** two pointers / stable partition. **O(n).**

---

## B. Strings

### 7. Valid Anagram
```java
boolean isAnagram(String s, String t) {
    if (s.length() != t.length()) return false;
    int[] count = new int[26];
    for (int i = 0; i < s.length(); i++) { count[s.charAt(i)-'a']++; count[t.charAt(i)-'a']--; }
    for (int c : count) if (c != 0) return false;
    return true;
}
```
**Pattern:** frequency count. **O(n).**

### 8. Valid Palindrome (ignore non-alphanumeric, case)
```java
boolean isPalindrome(String s) {
    int i = 0, j = s.length()-1;
    while (i < j) {
        while (i < j && !Character.isLetterOrDigit(s.charAt(i))) i++;
        while (i < j && !Character.isLetterOrDigit(s.charAt(j))) j--;
        if (Character.toLowerCase(s.charAt(i++)) != Character.toLowerCase(s.charAt(j--))) return false;
    }
    return true;
}
```
**Pattern:** two pointers from both ends. **O(n).**

### 9. Longest Substring Without Repeating Characters
```java
int lengthOfLongestSubstring(String s) {
    Map<Character,Integer> last = new HashMap<>();
    int start = 0, best = 0;
    for (int i = 0; i < s.length(); i++) {
        char c = s.charAt(i);
        if (last.containsKey(c) && last.get(c) >= start) start = last.get(c) + 1;
        last.put(c, i);
        best = Math.max(best, i - start + 1);
    }
    return best;
}
```
**Pattern:** sliding window + last-seen map. **O(n).**

### 10. Group Anagrams
```java
List<List<String>> groupAnagrams(String[] words) {
    Map<String,List<String>> m = new HashMap<>();
    for (String w : words) {
        char[] c = w.toCharArray(); Arrays.sort(c);
        m.computeIfAbsent(new String(c), k -> new ArrayList<>()).add(w);
    }
    return new ArrayList<>(m.values());
}
```
**Pattern:** sorted-string key. **O(n·k log k).**

### 11. First Non-Repeating Character
```java
int firstUniqChar(String s) {
    int[] count = new int[26];
    for (char c : s.toCharArray()) count[c-'a']++;
    for (int i = 0; i < s.length(); i++) if (count[s.charAt(i)-'a'] == 1) return i;
    return -1;
}
```

### 12. Reverse Words in a String
```java
String reverseWords(String s) {
    String[] parts = s.trim().split("\\s+");
    Collections.reverse(Arrays.asList(parts));
    return String.join(" ", parts);
}
```

### 13. String to Integer / Count occurrences / Check rotation
- **isRotation:** `(s1.length()==s2.length()) && (s1+s1).contains(s2)`.
- Know how to reverse a string in place with two pointers (char array).

---

## C. Two Pointers & Sliding Window

### 14. Container With Most Water
```java
int maxArea(int[] h) {
    int i = 0, j = h.length-1, best = 0;
    while (i < j) {
        best = Math.max(best, Math.min(h[i], h[j]) * (j - i));
        if (h[i] < h[j]) i++; else j--;   // move the shorter wall
    }
    return best;
}
```
**Pattern:** two pointers converging. **O(n).**

### 15. 3Sum (triplets summing to 0)
```java
List<List<Integer>> threeSum(int[] a) {
    Arrays.sort(a);
    List<List<Integer>> res = new ArrayList<>();
    for (int i = 0; i < a.length-2; i++) {
        if (i > 0 && a[i] == a[i-1]) continue;       // skip dup
        int l = i+1, r = a.length-1;
        while (l < r) {
            int sum = a[i] + a[l] + a[r];
            if (sum == 0) {
                res.add(Arrays.asList(a[i], a[l], a[r]));
                while (l < r && a[l]==a[l+1]) l++;
                while (l < r && a[r]==a[r-1]) r--;
                l++; r--;
            } else if (sum < 0) l++; else r--;
        }
    }
    return res;
}
```
**Pattern:** sort + two pointers. **O(n²).** Watch duplicate skipping.

### 16. Maximum Sum Subarray of size k (fixed window)
```java
int maxSum(int[] a, int k) {
    int sum = 0;
    for (int i = 0; i < k; i++) sum += a[i];
    int best = sum;
    for (int i = k; i < a.length; i++) { sum += a[i] - a[i-k]; best = Math.max(best, sum); }
    return best;
}
```
**Pattern:** fixed-size sliding window. **O(n).**

---

## D. Linked Lists

### 17. Reverse a Linked List
```java
ListNode reverse(ListNode head) {
    ListNode prev = null;
    while (head != null) { ListNode next = head.next; head.next = prev; prev = head; head = next; }
    return prev;
}
```

### 18. Detect Cycle (Floyd's) + find cycle start
```java
boolean hasCycle(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next; fast = fast.next.next;
        if (slow == fast) return true;
    }
    return false;
}
```
Follow-up: to find the start, after they meet, move one pointer to head and advance both by 1 until they meet again.

### 19. Merge Two Sorted Lists
```java
ListNode merge(ListNode a, ListNode b) {
    ListNode dummy = new ListNode(0), tail = dummy;
    while (a != null && b != null) {
        if (a.val <= b.val) { tail.next = a; a = a.next; }
        else { tail.next = b; b = b.next; }
        tail = tail.next;
    }
    tail.next = (a != null) ? a : b;
    return dummy.next;
}
```
**Pattern:** dummy head. Extends to "Merge K sorted lists" with a min-heap (**O(N log k)**).

### 20. Find Middle of Linked List (slow/fast)
```java
ListNode middle(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) { slow = slow.next; fast = fast.next.next; }
    return slow;
}
```

### 21. Remove Nth Node From End (two pointers, one gap of n)

---

## E. Stacks & Queues

### 22. Valid Parentheses
```java
boolean isValid(String s) {
    Deque<Character> st = new ArrayDeque<>();
    Map<Character,Character> pairs = Map.of(')','(', ']','[', '}','{');
    for (char c : s.toCharArray()) {
        if (pairs.containsValue(c)) st.push(c);
        else if (st.isEmpty() || st.pop() != pairs.get(c)) return false;
    }
    return st.isEmpty();
}
```

### 23. Min Stack (getMin in O(1))
```java
class MinStack {
    Deque<int[]> st = new ArrayDeque<>();   // {value, currentMin}
    void push(int x) { int min = st.isEmpty() ? x : Math.min(x, st.peek()[1]); st.push(new int[]{x, min}); }
    void pop() { st.pop(); }
    int top() { return st.peek()[0]; }
    int getMin() { return st.peek()[1]; }
}
```

### 24. Implement Queue using two Stacks (classic).

---

## F. Trees

### 25. Level Order Traversal (BFS)
```java
List<List<Integer>> levelOrder(TreeNode root) {
    List<List<Integer>> res = new ArrayList<>();
    if (root == null) return res;
    Queue<TreeNode> q = new LinkedList<>(); q.add(root);
    while (!q.isEmpty()) {
        int n = q.size(); List<Integer> level = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            TreeNode t = q.poll(); level.add(t.val);
            if (t.left != null) q.add(t.left);
            if (t.right != null) q.add(t.right);
        }
        res.add(level);
    }
    return res;
}
```

### 26. Max Depth / Height of Binary Tree
```java
int maxDepth(TreeNode root) {
    if (root == null) return 0;
    return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
}
```

### 27. Validate BST
```java
boolean isValidBST(TreeNode root) { return valid(root, Long.MIN_VALUE, Long.MAX_VALUE); }
boolean valid(TreeNode n, long lo, long hi) {
    if (n == null) return true;
    if (n.val <= lo || n.val >= hi) return false;
    return valid(n.left, lo, n.val) && valid(n.right, n.val, hi);
}
```

### 28. Invert Binary Tree
```java
TreeNode invert(TreeNode root) {
    if (root == null) return null;
    TreeNode l = invert(root.left), r = invert(root.right);
    root.left = r; root.right = l;
    return root;
}
```

### 29. Lowest Common Ancestor (BST version — easy)
```java
TreeNode lca(TreeNode root, TreeNode p, TreeNode q) {
    while (root != null) {
        if (p.val < root.val && q.val < root.val) root = root.left;
        else if (p.val > root.val && q.val > root.val) root = root.right;
        else return root;
    }
    return null;
}
```

---

## G. Searching & Sorting

### 30. Binary Search
```java
int binarySearch(int[] a, int target) {
    int lo = 0, hi = a.length - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;         // avoid overflow
        if (a[mid] == target) return mid;
        else if (a[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
```
**O(log n).** Also know: search in **rotated sorted array**, first/last position.

### 31. Kth Largest Element (min-heap of size k)
```java
int findKthLargest(int[] nums, int k) {
    PriorityQueue<Integer> pq = new PriorityQueue<>();  // min-heap
    for (int x : nums) { pq.offer(x); if (pq.size() > k) pq.poll(); }
    return pq.peek();
}
```
**O(n log k).** (QuickSelect gives average O(n).)

### 32. Merge Intervals
```java
int[][] merge(int[][] iv) {
    Arrays.sort(iv, (a,b) -> a[0]-b[0]);
    List<int[]> out = new ArrayList<>();
    for (int[] cur : iv) {
        if (out.isEmpty() || out.get(out.size()-1)[1] < cur[0]) out.add(cur);
        else out.get(out.size()-1)[1] = Math.max(out.get(out.size()-1)[1], cur[1]);
    }
    return out.toArray(new int[0][]);
}
```
**O(n log n).** Related: "Meeting Rooms" (min rooms needed → sort starts/ends or min-heap).

---

## H. Recursion & Backtracking

### 33. Fibonacci (memoized) / Climbing Stairs
```java
int climbStairs(int n) {
    int a = 1, b = 1;                 // ways to reach step i
    for (int i = 2; i <= n; i++) { int c = a + b; a = b; b = c; }
    return b;
}
```

### 34. Subsets (power set)
```java
List<List<Integer>> subsets(int[] nums) {
    List<List<Integer>> res = new ArrayList<>();
    backtrack(nums, 0, new ArrayList<>(), res);
    return res;
}
void backtrack(int[] nums, int start, List<Integer> cur, List<List<Integer>> res) {
    res.add(new ArrayList<>(cur));
    for (int i = start; i < nums.length; i++) {
        cur.add(nums[i]);
        backtrack(nums, i+1, cur, res);
        cur.remove(cur.size()-1);          // undo (backtrack)
    }
}
```
**Pattern:** choose → recurse → un-choose. Same template for **permutations, combinations, N-Queens**.

---

## I. Dynamic Programming (know 3–4 well)

### 35. Coin Change (min coins)
```java
int coinChange(int[] coins, int amount) {
    int[] dp = new int[amount+1];
    Arrays.fill(dp, amount+1); dp[0]=0;
    for (int i = 1; i <= amount; i++)
        for (int c : coins) if (c <= i) dp[i] = Math.min(dp[i], dp[i-c]+1);
    return dp[amount] > amount ? -1 : dp[amount];
}
```

### 36. Longest Increasing Subsequence — DP O(n²) or patience sorting O(n log n).
### 37. 0/1 Knapsack — classic 2D DP (weights/values).
### 38. Edit Distance / Longest Common Subsequence — 2D DP grid.
**DP recipe:** define the state, the recurrence (transition), base cases, and order of filling. Say this out loud.

---

## J. Graphs (know BFS/DFS + one more)

### 39. Number of Islands (DFS flood fill)
```java
int numIslands(char[][] g) {
    int count = 0;
    for (int i=0;i<g.length;i++) for (int j=0;j<g[0].length;j++)
        if (g[i][j]=='1') { dfs(g,i,j); count++; }
    return count;
}
void dfs(char[][] g,int i,int j){
    if(i<0||j<0||i>=g.length||j>=g[0].length||g[i][j]!='1') return;
    g[i][j]='0';
    dfs(g,i+1,j); dfs(g,i-1,j); dfs(g,i,j+1); dfs(g,i,j-1);
}
```

### 40. Course Schedule / Topological Sort (detect cycle in a DAG via BFS Kahn's algorithm or DFS).
### 41. Clone Graph / Shortest path in unweighted grid (BFS).

---

## K. SQL Coding (they often ask 1–2 — see file 08 for more)
```sql
-- Nth highest salary
SELECT DISTINCT salary FROM emp ORDER BY salary DESC LIMIT 1 OFFSET N-1;

-- Employees earning more than their manager
SELECT e.name FROM emp e JOIN emp m ON e.manager_id = m.id WHERE e.salary > m.salary;

-- Department with highest average salary
SELECT dept_id, AVG(salary) a FROM emp GROUP BY dept_id ORDER BY a DESC LIMIT 1;

-- Second highest salary (handles no-second-value with NULL)
SELECT MAX(salary) FROM emp WHERE salary < (SELECT MAX(salary) FROM emp);

-- Duplicate emails
SELECT email FROM person GROUP BY email HAVING COUNT(*) > 1;
```

---

## L. Java-specific "write code" questions (very common in Java interviews)
- **Reverse a string without a library** (two-pointer char array swap).
- **Check if a number is prime / Fibonacci / factorial (iterative & recursive).**
- **Find the missing number in 1..n** → `n*(n+1)/2 - sum(array)`.
- **Count word frequency in a sentence** → `Map<String,Integer>` + `merge(w,1,Integer::sum)`.
- **Remove duplicates from a list** → `new ArrayList<>(new LinkedHashSet<>(list))` (keeps order).
- **Sort a `Map` by value** → stream `entrySet().stream().sorted(Map.Entry.comparingByValue())`.
- **Find second largest element** in one pass (track largest + secondLargest).
- **Reverse a number** → repeatedly `rev = rev*10 + n%10; n/=10;`.
- **FizzBuzz** (yes, still asked) — multiples of 3 → "Fizz", 5 → "Buzz", both → "FizzBuzz".
- **Anagram / palindrome checks** (above).
- **Java 8 streams task:** e.g., "given a list of employees, group by department and get highest paid per department" (know `groupingBy` + `maxBy`).

```java
// Group employees, highest paid per dept (Java 8 — commonly asked)
Map<String, Optional<Employee>> topPerDept = employees.stream()
    .collect(Collectors.groupingBy(Employee::getDept,
             Collectors.maxBy(Comparator.comparingDouble(Employee::getSalary))));
```

---

## 🎯 The 15 to practice writing from scratch (highest ROI)
1. Two Sum  2. Max Subarray (Kadane)  3. Longest Substring w/o Repeat  4. Valid Anagram
5. Valid Palindrome  6. Merge Intervals  7. Reverse Linked List  8. Detect Cycle
9. Valid Parentheses  10. Level Order (BFS)  11. Binary Search  12. Kth Largest (heap)
13. Number of Islands (DFS)  14. Coin Change (DP)  15. Subsets (backtracking)

## 🗣️ How to talk while coding (scoring points)
- "The brute force is O(n²); I can use a hashmap to get O(n)."
- "Let me handle edge cases: empty input, one element, duplicates, negatives, overflow."
- "I'll use `lo + (hi-lo)/2` to avoid integer overflow."
- "Time is O(n), space is O(n) for the map — I could reduce space if needed."
- Always **test your code** with a small example by hand before saying "done."
