def bubbleSort(arr):
    n = len(arr)
    for i in range(n-1):
        for j in range(0,n-i-1):
            if arr[j][0] > arr[j+1][0]:
                arr[j], arr[j+1] = arr[j+1], arr[j]