"use client";

import { useEffect, useRef } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import { fetchReviewsPage, type ReviewsPage } from "@/lib/api/reviews";
import { ReviewCard } from "./ReviewCard";
import { Button } from "@/components/ui/Button";

export function ReviewList({ initialPage }: { initialPage: ReviewsPage }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const sentinelRef = useRef<HTMLDivElement>(null);

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isFetchNextPageError,
  } = useInfiniteQuery({
    queryKey: ["reviews"],
    queryFn: ({ pageParam }) => fetchReviewsPage(pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage) =>
      lastPage.page * lastPage.page_size < lastPage.total
        ? lastPage.page + 1
        : undefined,
    initialData: { pages: [initialPage], pageParams: [1] },
    staleTime: 60_000,
  });

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel || !hasNextPage || isFetchNextPageError) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { root: scrollRef.current, rootMargin: "200px" },
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasNextPage, isFetchingNextPage, isFetchNextPageError, fetchNextPage]);

  const reviews = data.pages.flatMap((page) => page.items);

  return (
    <div
      ref={scrollRef}
      role="region"
      aria-label="Customer reviews"
      tabIndex={0}
      className="max-h-[420px] overflow-y-auto rounded-2xl p-1 md:max-h-[520px]"
    >
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {reviews.map((review) => (
          <ReviewCard key={review.id} review={review} />
        ))}
      </div>

      {hasNextPage ? (
        <div ref={sentinelRef} className="flex justify-center py-8">
          {isFetchNextPageError ? (
            <Button variant="secondary" onClick={() => fetchNextPage()}>
              Couldn&apos;t load more. Try again
            </Button>
          ) : (
            <Loader2
              className="animate-spin text-forest"
              aria-label="Loading more reviews"
            />
          )}
        </div>
      ) : (
        <p className="py-8 text-center text-sm text-muted">
          That&apos;s all {data.pages[0].total} reviews
        </p>
      )}
    </div>
  );
}
