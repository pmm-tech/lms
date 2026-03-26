<template>
    <div class="relative flex h-full flex-col">
        <div class="h-full flex-1">
            <div class="flex text-base bg-surface-white" :class="isInIframe ? 'h-fit' : 'h-screen'">
                <div class="w-full overflow-auto" id="scrollContainer">
                    <slot />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
const isInIframe = window.self !== window.top
</script>